"""Bind Designer companion controls to validated persistent runtime policy."""

from dataclasses import asdict, replace
import sqlite3

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QLabel, QMessageBox

from core.companion_policy import CompanionPolicy
from core.conversation import ConversationManager
from storage.companion_policy_repository import CompanionPolicyRepository


# Keep existing Designer object names, including their spelling differences.
INTEGER_FIELDS = {
    "recent_messages": ("recentMessagesEdit", "消息条目数", 1, 2147483647, "条"),
    "history_page_size": ("historyPageSizeEdit", "加载历史条目数", 1, 2147483647, "条"),
    "summary_batch_size": ("summaryBatchSizeEdit", "摘要处理旧条目数", 2, 2147483647, "条"),
    "summary_count": ("summaryCountEdit", "摘要数量", 1, 2147483647, "份"),
    "summary_max_chars": ("summaryMaxCharsEdit", "摘要最大字符数", 1, 2147483647, "字符"),
    "context_max_chars": ("contestMaxCharsEdit", "单次对话上限字符", 2000, 2147483647, "字符"),
    "followup_delay_days": ("followupDedlayDaysEdit", "跟进等待天数", 1, 2147483647, "天"),
    "followup_cooldown_days": ("followupCooldownDaysEdit", "同一话题跟进间隔", 1, 2147483647, "天"),
    "followup_expiry_days": ("followExpiryDaysEdit", "事项有效期", 1, 2147483647, "天"),
    "followup_idle_seconds": ("followupIdleSecondsEdit", "空闲触发时长", 0, 2147483647, "秒"),
    "quiet_start_hour": ("quietStartHourEdit", "静默开始时间", 0, 23, "北京时间整点 0–23"),
    "quiet_end_hour": ("quietEndHourEdit", "静默结束时间", 0, 23, "北京时间整点 0–23"),
}


class CompanionSettingsController(QObject):
    policy_saved = Signal()

    def __init__(self, window, ui, repository: CompanionPolicyRepository,
                 conversation_manager: ConversationManager) -> None:
        super().__init__(window)
        self._window = window
        self._ui = ui
        self._repository = repository
        self._manager = conversation_manager
        self._busy = False
        self._status = QLabel(window)
        self._status.setWordWrap(True)
        self._ui.gridLayout_4.addWidget(self._status, 3, 0, 1, 2)
        self._last_effective = self._manager.followups_enabled
        self._ui.followupsEnabledBox.clear()
        self._ui.followupsEnabledBox.addItem("开启", True)
        self._ui.followupsEnabledBox.addItem("关闭", False)
        try:
            comments = self._repository.comments()
        except (ValueError, OSError, UnicodeError):
            comments = {}
        for name, (widget_name, label, minimum, maximum, unit) in INTEGER_FIELDS.items():
            widget = getattr(self._ui, widget_name)
            widget.setValidator(QIntValidator(minimum, maximum, widget))
            widget.setPlaceholderText(unit)
            widget.setToolTip(comments.get(name, f"{label}，单位：{unit}。范围 {minimum}–{maximum}。"))
        self._ui.followupsEnabledBox.setToolTip(comments.get("followups_enabled", "控制主动关心功能。"))
        self._ui.saveCompanionButton.clicked.connect(self.save)
        self._ui.recoveryCompanionButton.clicked.connect(self.restore_defaults)
        self._ui.tabWidget.currentChanged.connect(self.refresh_followup_state)
        self._set_fields(replace(self._manager.policy, followups_enabled=self._last_effective))
        self._set_status("配置已加载；修改后点击保存即可生效。")

    def _set_status(self, text: str) -> None:
        self._status.setText(text)
        self._ui.statusLabel.setText(text)

    def _set_fields(self, policy: CompanionPolicy) -> None:
        for name, value in asdict(policy).items():
            if name in INTEGER_FIELDS:
                getattr(self._ui, INTEGER_FIELDS[name][0]).setText(str(value))
        box = self._ui.followupsEnabledBox
        box.setCurrentIndex(box.findData(policy.followups_enabled))

    def _from_fields(self) -> CompanionPolicy:
        values = {}
        for name, (widget_name, label, minimum, maximum, unit) in INTEGER_FIELDS.items():
            widget = getattr(self._ui, widget_name)
            text = widget.text().strip()
            if not text or not text.isascii() or not text.isdecimal():
                widget.setFocus()
                raise ValueError(f"{label}必须填写整数（单位：{unit}）。")
            value = int(text)
            if not minimum <= value <= maximum:
                widget.setFocus()
                raise ValueError(f"{label}需在 {minimum}–{maximum} 范围内（单位：{unit}）。")
            values[name] = value
        enabled = self._ui.followupsEnabledBox.currentData()
        if not isinstance(enabled, bool):
            raise ValueError("请选择是否开启主动关心。")
        values["followups_enabled"] = enabled
        policy = CompanionPolicy(**values)
        policy.validate()
        return policy

    def save(self) -> None:
        if self._busy:
            self._set_status("请等待当前请求结束后再保存。")
            return
        try:
            policy = self._from_fields()
            previous = self._repository.load()
            self._repository.save(policy)
            try:
                self._manager.apply_policy(policy)
            except Exception:
                # Runtime/db preferences failed: restore the previous file policy.
                self._repository.save(previous)
                raise
        except ValueError as error:
            self._set_status(str(error))
            QMessageBox.warning(self._window, "交互配置无效", str(error))
            return
        except (OSError, UnicodeError, sqlite3.Error):
            self._set_status("保存失败，请检查配置文件和数据库的读写权限。")
            QMessageBox.warning(self._window, "保存失败", self._status.text())
            return
        self._last_effective = self._manager.followups_enabled
        self._set_fields(policy)
        self._set_status("交互配置已保存并生效。已有事项的到期时间保留，新事项使用新的等待天数。")
        self.policy_saved.emit()

    def restore_defaults(self) -> None:
        if self._busy:
            return
        self._set_fields(CompanionPolicy())
        self._set_status("已回填默认值，尚未保存；点击保存配置后生效。")

    def refresh_followup_state(self, *_args) -> None:
        """Reflect chat opt-out without overwriting an unsaved combo-box edit."""
        enabled = self._manager.followups_enabled
        box = self._ui.followupsEnabledBox
        if box.currentData() == self._last_effective and enabled != self._last_effective:
            box.setCurrentIndex(box.findData(enabled))
        self._last_effective = enabled

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._ui.saveCompanionButton.setEnabled(not busy)
        self._ui.recoveryCompanionButton.setEnabled(not busy)
