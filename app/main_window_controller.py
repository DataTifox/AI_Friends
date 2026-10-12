"""Controller for main-window interactions."""

from __future__ import annotations

from html import escape
import sqlite3
import time

from PySide6.QtCore import QEvent, QObject, Qt, QThreadPool, QTimer
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMessageBox, QPushButton

from app.background_task import BackgroundTask
from app.companion_settings_controller import CompanionSettingsController
from core.conversation import ConversationManager
from core.llm_settings import LLMSettings
from core.time_utils import display_time
from storage.repository import Message
from storage.settings_repository import SettingsRepository
from storage.companion_policy_repository import CompanionPolicyRepository


class MainWindowController(QObject):
    """Connect the generated main-window widgets to application behavior."""

    def __init__(
        self,
        window,
        ui,
        settings_repository: SettingsRepository,
        conversation_manager: ConversationManager,
        policy_repository: CompanionPolicyRepository | None = None,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._ui = ui
        self._settings_repository = settings_repository
        self._conversation_manager = conversation_manager
        self._conversation_id: int | None = None
        self._visible_messages: list[Message] = []
        self._busy = False
        self._task = None
        self._task_kind = "chat"
        self._last_activity = time.monotonic()
        self._next_followup_attempt = 0.0
        self._history_exhausted = False
        self._rendering = False
        self._companion_settings = None
        self._history_button = QPushButton("加载更早记录", window)
        self._ui.verticalLayout.insertWidget(1, self._history_button)
        self._history_button.clicked.connect(self.load_older_messages)
        self._ui.inputWindow.textChanged.connect(self._record_activity)
        self._ui.showWindow.verticalScrollBar().valueChanged.connect(self._history_scrolled)

        self._ui.LLMSaveButton.clicked.connect(self.save_llm_settings)
        self._ui.LLMCleanButton.clicked.connect(self.clear_llm_fields)
        self._ui.sendButton.clicked.connect(self.send_user_message)
        self._ui.inputWindow.installEventFilter(self)
        self.load_llm_settings()
        self.open_recent_conversation()
        if policy_repository is not None:
            self._companion_settings = CompanionSettingsController(
                window, ui, policy_repository, conversation_manager
            )
            self._companion_settings.policy_saved.connect(self._policy_saved)
        self._followup_timer = QTimer(self)
        self._followup_timer.setInterval(30000)
        self._followup_timer.timeout.connect(self.check_followup)
        self._followup_timer.start()

    def load_llm_settings(self) -> None:
        """Load saved settings into the configuration form on application startup."""
        try:
            settings = self._settings_repository.load()
        except (OSError, UnicodeError):
            self._set_llm_status("模型配置读取失败，请检查 .env 文件。")
            return
        self._set_llm_fields(settings)
        self._set_llm_status(
            "模型配置已加载。" if not settings.missing_fields() else "模型配置未填写完整，请填写后保存。"
        )

    def save_llm_settings(self) -> None:
        """Validate and persist the values currently shown in the form."""
        settings = self._settings_from_form()
        try:
            self._settings_repository.save(settings)
        except ValueError as error:
            message = str(error)
            self._set_llm_status(message)
            QMessageBox.warning(self._window, "模型配置无效", message)
            return
        except OSError as error:
            message = f"保存模型配置失败：{error}"
            self._set_llm_status(message)
            QMessageBox.critical(self._window, "保存失败", message)
            return

        self._set_llm_status("模型配置已保存。")

    def clear_llm_fields(self) -> None:
        """Clear the form only; the saved .env file remains unchanged until saving."""
        self._set_llm_fields(LLMSettings())
        self._set_llm_status("已清空输入框，已保存的模型配置未修改。")

    def _set_llm_status(self, message: str) -> None:
        """Keep feedback visible in the model settings page after button actions."""
        self._ui.llmStatusLabel.setText(message)
        self.set_status(message)

    def open_recent_conversation(self) -> None:
        """Load the latest conversation and its saved messages into the chat view."""
        conversation = self._conversation_manager.open_recent_or_create()
        self._conversation_id = conversation.id
        self._visible_messages = self._conversation_manager.load_messages(conversation.id)
        self._history_exhausted = len(self._visible_messages) < self._conversation_manager.policy.history_page_size
        self._render_history()
        self.set_status("已打开最近会话。")

    def send_user_message(self) -> None:
        """Persist the input text and show it immediately in the conversation."""
        if self._busy:
            return
        content = self._ui.inputWindow.toPlainText().strip()
        if not content:
            self.set_status("请输入消息后再发送。")
            return
        if self._conversation_id is None:
            self.set_status("当前会话尚未初始化。")
            return

        try:
            self._settings_repository.load().validate()
            user_message = self._conversation_manager.record_user_message(self._conversation_id, content)
        except (ValueError, OSError, UnicodeError, sqlite3.Error) as error:
            self.set_status(str(error))
            return
        self._append_stored_message(user_message)
        if self._companion_settings:
            self._companion_settings.refresh_followup_state()
        self._ui.inputWindow.clear()
        conversation_id = self._conversation_id
        self._start_task(lambda: self._conversation_manager.reply_to_user_message(conversation_id), "chat")

    def set_status(self, message: str) -> None:
        """Display the current application state in the chat tab."""
        self._ui.statusLabel.setText(message)

    def _message_html(self, message: Message) -> str:
        speaker = "你" if message.role == "user" else self._conversation_manager.assistant_name
        return (f"<p><b>{escape(speaker)}：</b> <span style='color:#888'>"
                f"{display_time(message.created_at)}</span><br>"
                f"{escape(message.content).replace(chr(10), '<br>')}</p>")

    def _append_stored_message(self, message: Message) -> None:
        self._visible_messages.append(message)
        self._rendering = True
        try:
            self._ui.showWindow.append(self._message_html(message))
            scroll = self._ui.showWindow.verticalScrollBar()
            scroll.setValue(scroll.maximum())
        finally:
            self._rendering = False

    def _render_history(self) -> None:
        self._rendering = True
        try:
            self._ui.showWindow.setHtml("".join(self._message_html(message) for message in self._visible_messages))
            self._history_button.setVisible(not self._history_exhausted)
            scroll = self._ui.showWindow.verticalScrollBar()
            scroll.setValue(scroll.maximum())
        finally:
            self._rendering = False

    def load_older_messages(self) -> None:
        if self._history_exhausted or not self._visible_messages or self._conversation_id is None:
            return
        scroll = self._ui.showWindow.verticalScrollBar()
        old_max, old_value = scroll.maximum(), scroll.value()
        try:
            older = self._conversation_manager.load_messages(self._conversation_id, self._visible_messages[0].id)
        except (sqlite3.Error, OSError):
            self.set_status("更早的记录暂时读取失败。")
            return
        self._history_exhausted = len(older) < self._conversation_manager.policy.history_page_size
        self._visible_messages = older + self._visible_messages
        self._render_history()
        self._rendering = True
        scroll.setValue(old_value + scroll.maximum() - old_max)
        self._rendering = False

    def _history_scrolled(self, value: int) -> None:
        if not self._rendering:
            self._record_activity()
            if value == 0 and self._ui.showWindow.verticalScrollBar().maximum() > 0:
                self.load_older_messages()

    def _record_activity(self) -> None:
        self._last_activity = time.monotonic()

    def _policy_saved(self) -> None:
        self._record_activity()
        if self._conversation_id is not None and self._visible_messages:
            try:
                self._history_exhausted = not self._conversation_manager.has_older_messages(
                    self._conversation_id, self._visible_messages[0].id
                )
                self._history_button.setVisible(not self._history_exhausted)
            except (sqlite3.Error, OSError):
                self.set_status("配置已保存；更早记录的读取状态暂时无法更新。")

    def _start_task(self, action, kind: str) -> None:
        self._busy = True
        self._task_kind = kind
        self._ui.sendButton.setEnabled(False)
        self._ui.LLMSaveButton.setEnabled(False)
        if self._companion_settings:
            self._companion_settings.set_busy(True)
        self.set_status("正在思考…" if kind == "chat" else "正在想起最近的话题…")
        self._task = BackgroundTask(action)
        self._task.signals.result.connect(self._task_result, Qt.ConnectionType.QueuedConnection)
        self._task.signals.error.connect(self._task_error, Qt.ConnectionType.QueuedConnection)
        self._task.signals.finished.connect(self._task_finished, Qt.ConnectionType.QueuedConnection)
        QThreadPool.globalInstance().start(self._task)

    def _task_result(self, message) -> None:
        if message is not None:
            self._append_stored_message(message)
        self.set_status("回复完成。" if self._task_kind == "chat" else "最近的话题已跟进。")

    def _task_error(self, message: str) -> None:
        self.set_status(message)
        if self._task_kind == "followup":
            self._next_followup_attempt = time.monotonic() + 3600
        else:
            QMessageBox.warning(self._window, "无法获取 AI 回复", message)

    def _task_finished(self) -> None:
        self._busy = False
        self._task = None
        self._ui.sendButton.setEnabled(True)
        self._ui.LLMSaveButton.setEnabled(True)
        if self._companion_settings:
            self._companion_settings.set_busy(False)
        self._record_activity()

    def check_followup(self) -> None:
        """Initiate only in an active, idle chat, while the input is empty."""
        if (self._busy or self._conversation_id is None or not self._window.isActiveWindow()
                or self._ui.tabWidget.currentWidget() is not self._ui.dialogueTab
                or self._ui.inputWindow.toPlainText().strip()
                or time.monotonic() < self._next_followup_attempt
                or time.monotonic() - self._last_activity < self._conversation_manager.policy.followup_idle_seconds):
            return
        try:
            self._settings_repository.load().validate()
            if not self._conversation_manager.has_due_followup():
                return
        except (ValueError, OSError, UnicodeError, sqlite3.Error):
            return
        conversation_id = self._conversation_id
        self._start_task(lambda: self._conversation_manager.proactive_message(conversation_id), "followup")

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Send on Enter while preserving Shift+Enter for newline input."""
        ui = getattr(self, "_ui", None)
        if ui is None:
            # Qt may deliver destruction events after Python attributes are cleared.
            return False
        if watched is ui.inputWindow and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if isinstance(key_event, QKeyEvent) and key_event.key() in {
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            }:
                if not key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.send_user_message()
                    return True
        return super().eventFilter(watched, event)

    def _settings_from_form(self) -> LLMSettings:
        return LLMSettings(
            provider=self._ui.provider_Edit.text(),
            api_key=self._ui.apiKeyEdit.text(),
            base_url=self._ui.baseUrlEdit.text(),
            model=self._ui.modelEdit.text(),
        )

    def _set_llm_fields(self, settings: LLMSettings) -> None:
        self._ui.provider_Edit.setText(settings.provider)
        self._ui.apiKeyEdit.setText(settings.api_key)
        self._ui.baseUrlEdit.setText(settings.base_url)
        self._ui.modelEdit.setText(settings.model)
