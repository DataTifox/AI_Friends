"""Controller for main-window interactions."""

from __future__ import annotations

from html import escape

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QMessageBox

from core.conversation import ConversationManager
from core.llm_settings import LLMSettings
from services.llm.base import LLMError
from storage.settings_repository import SettingsRepository


class MainWindowController(QObject):
    """Connect the generated main-window widgets to application behavior."""

    def __init__(
        self,
        window,
        ui,
        settings_repository: SettingsRepository,
        conversation_manager: ConversationManager,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._ui = ui
        self._settings_repository = settings_repository
        self._conversation_manager = conversation_manager
        self._conversation_id: int | None = None

        self._ui.LLMSaveButton.clicked.connect(self.save_llm_settings)
        self._ui.LLMCleanButton.clicked.connect(self.clear_llm_fields)
        self._ui.sendButton.clicked.connect(self.send_user_message)
        self._ui.inputWindow.installEventFilter(self)
        self.load_llm_settings()
        self.open_recent_conversation()

    def load_llm_settings(self) -> None:
        """Load saved settings into the configuration form on application startup."""
        self._set_llm_fields(self._settings_repository.load())
        self.set_status("模型配置已加载。")

    def save_llm_settings(self) -> None:
        """Validate and persist the values currently shown in the form."""
        settings = self._settings_from_form()
        try:
            self._settings_repository.save(settings)
        except ValueError as error:
            message = str(error)
            self.set_status(message)
            QMessageBox.warning(self._window, "模型配置无效", message)
            return
        except OSError as error:
            message = f"保存模型配置失败：{error}"
            self.set_status(message)
            QMessageBox.critical(self._window, "保存失败", message)
            return

        self.set_status("模型配置已保存。")

    def clear_llm_fields(self) -> None:
        """Clear the form only; the saved .env file remains unchanged until saving."""
        self._set_llm_fields(LLMSettings())
        self.set_status("已清空输入框，尚未保存。")

    def open_recent_conversation(self) -> None:
        """Load the latest conversation and its saved messages into the chat view."""
        conversation = self._conversation_manager.open_recent_or_create()
        self._conversation_id = conversation.id
        self._ui.showWindow.clear()
        for message in self._conversation_manager.load_messages(conversation.id):
            self.append_message(message.role, message.content)
        self.set_status("已打开最近会话。")

    def send_user_message(self) -> None:
        """Persist the input text and show it immediately in the conversation."""
        content = self._ui.inputWindow.toPlainText().strip()
        if not content:
            self.set_status("请输入消息后再发送。")
            return
        if self._conversation_id is None:
            self.set_status("当前会话尚未初始化。")
            return

        user_message = self._conversation_manager.record_user_message(
            self._conversation_id, content
        )
        self.append_message(user_message.role, user_message.content)
        self._ui.inputWindow.clear()
        self._ui.sendButton.setEnabled(False)
        self.set_status("正在思考…")
        QApplication.processEvents()
        try:
            assistant_message = self._conversation_manager.reply_to_user_message(
                self._conversation_id
            )
        except LLMError as error:
            message = str(error)
            self.set_status(message)
            QMessageBox.warning(self._window, "无法获取 AI 回复", message)
        except OSError as error:
            message = f"保存聊天记录失败：{error}"
            self.set_status(message)
            QMessageBox.critical(self._window, "聊天失败", message)
        else:
            self.append_message(assistant_message.role, assistant_message.content)
            self.set_status("回复完成。")
        finally:
            self._ui.sendButton.setEnabled(True)

    def set_status(self, message: str) -> None:
        """Display the current application state in the chat tab."""
        self._ui.statusLabel.setText(message)

    def append_message(self, role: str, content: str) -> None:
        """Render one stored message safely in the read-only chat text area."""
        speaker = "你" if role == "user" else self._conversation_manager.assistant_name
        safe_content = escape(content).replace("\n", "<br>")
        self._ui.showWindow.append(f"<p><b>{speaker}：</b>{safe_content}</p>")

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Send on Enter while preserving Shift+Enter for newline input."""
        if watched is self._ui.inputWindow and event.type() == QEvent.Type.KeyPress:
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
