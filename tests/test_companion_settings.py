"""Offline coverage for Designer configuration controls and live policy updates."""

from dataclasses import asdict, replace
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QMainWindow

from app.main_window_controller import MainWindowController
from app.companion_settings_controller import INTEGER_FIELDS
from core.companion_policy import CompanionPolicy
from core.conversation import ConversationManager
from core.followup import FollowupManager
from core.memory import MemoryManager
from core.personality import PersonalityManager
from core.summary import SummaryManager
from storage.companion_policy_repository import CompanionPolicyRepository
from storage.database import Database
from storage.followup_repository import FollowupRepository
from storage.repository import ConversationRepository, MemoryRepository
from storage.settings_repository import SettingsRepository
from storage.summary_repository import SummaryRepository
from ui.generated.main_window import Ui_MainWindow

PROJECT = Path(__file__).resolve().parents[1]


class CompanionSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.path = self.root / "companion.json"
        document = {"_comments": {"recent_messages": "每次发给模型的消息条数。"}, **asdict(CompanionPolicy())}
        self.path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.policy_repository = CompanionPolicyRepository(self.path)
        self.database = Database(self.root / "companion.db")
        self.database.initialize()
        self.messages = ConversationRepository(self.database)
        self.followup_repository = FollowupRepository(self.database)
        policy = self.policy_repository.load()
        self.summaries = SummaryManager(self.messages, SummaryRepository(self.database), policy)
        self.followups = FollowupManager(self.followup_repository, policy)
        self.manager = ConversationManager(
            self.messages, SettingsRepository(self.root / ".env"),
            PersonalityManager(PROJECT / "config/personality.json"),
            MemoryManager(MemoryRepository(self.database)), lambda settings: None,
            self.summaries, self.followups, policy,
        )
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.main_controller = MainWindowController(
            self.window, self.ui, SettingsRepository(self.root / ".env"),
            self.manager, self.policy_repository,
        )
        self.window.controller = self.main_controller
        self.main_controller._followup_timer.stop()
        self.controller = self.main_controller._companion_settings

    def tearDown(self):
        self.window.close()
        self.directory.cleanup()

    def fill(self, policy):
        for name, value in asdict(policy).items():
            if name in INTEGER_FIELDS:
                getattr(self.ui, INTEGER_FIELDS[name][0]).setText(str(value))
        self.ui.followupsEnabledBox.setCurrentIndex(self.ui.followupsEnabledBox.findData(policy.followups_enabled))

    def test_startup_loads_every_field_and_comment_tooltips(self):
        policy = self.manager.policy
        for name, (widget_name, _, _, _, _) in INTEGER_FIELDS.items():
            self.assertEqual(getattr(self.ui, widget_name).text(), str(getattr(policy, name)))
            self.assertIsNotNone(getattr(self.ui, widget_name).validator())
        self.assertEqual(self.ui.followupsEnabledBox.count(), 2)
        self.assertIs(self.ui.followupsEnabledBox.currentData(), True)
        self.assertEqual(self.ui.recentMessagesEdit.toolTip(), "每次发给模型的消息条数。")

    def test_save_updates_all_runtime_components_preserves_comments_and_reloads(self):
        policy = CompanionPolicy(6, 20, 8, 2, 300, 3000, False, 4, 5, 14, 0, 21, 8)
        self.fill(policy)
        self.ui.saveCompanionButton.click()
        self.assertEqual(self.policy_repository.load(), policy)
        self.assertEqual(self.manager.policy, policy)
        self.assertEqual(self.summaries._policy, policy)
        self.assertEqual(self.followups._policy, policy)
        self.assertFalse(self.followup_repository.enabled())
        self.assertFalse(self.manager.followups_enabled)
        self.assertEqual(self.policy_repository.comments()["recent_messages"], "每次发给模型的消息条数。")
        restarted = CompanionPolicyRepository(self.path)
        self.assertEqual(restarted.load(), policy)
        self.assertIn("已保存并生效", self.controller._status.text())

    def test_restore_defaults_only_changes_form_until_saved(self):
        policy = replace(CompanionPolicy(), recent_messages=4, followups_enabled=False)
        self.fill(policy)
        self.ui.saveCompanionButton.click()
        saved = self.path.read_bytes()
        self.ui.recoveryCompanionButton.click()
        self.assertEqual(self.ui.recentMessagesEdit.text(), "12")
        self.assertIs(self.ui.followupsEnabledBox.currentData(), True)
        self.assertEqual(self.path.read_bytes(), saved)
        self.assertEqual(self.manager.policy, policy)
        self.ui.saveCompanionButton.click()
        self.assertEqual(self.policy_repository.load(), CompanionPolicy())
        self.assertTrue(self.manager.followups_enabled)

    def test_invalid_empty_and_out_of_range_values_do_not_save(self):
        original = self.path.read_bytes()
        for widget_name, invalid in (
            ("recentMessagesEdit", ""), ("recentMessagesEdit", "1.5"),
            ("summaryBatchSizeEdit", "1"), ("contestMaxCharsEdit", "1999"),
            ("quietStartHourEdit", "24"), ("quietEndHourEdit", "-1"),
        ):
            with self.subTest(widget=widget_name, value=invalid):
                self.fill(CompanionPolicy())
                getattr(self.ui, widget_name).setText(invalid)
                with patch("app.companion_settings_controller.QMessageBox.warning") as warning:
                    self.ui.saveCompanionButton.click()
                    warning.assert_called_once()
                self.assertEqual(self.path.read_bytes(), original)
                self.assertEqual(self.manager.policy, CompanionPolicy())

    def test_chat_opt_out_is_reflected_and_ui_save_can_enable(self):
        conversation = self.manager.open_recent_or_create()
        self.manager.record_user_message(conversation.id, "关闭主动关心。")
        self.ui.tabWidget.setCurrentWidget(self.ui.dialogueTab)
        self.ui.tabWidget.setCurrentWidget(self.ui.companionTab)
        self.assertIs(self.ui.followupsEnabledBox.currentData(), False)
        self.ui.followupsEnabledBox.setCurrentIndex(self.ui.followupsEnabledBox.findData(True))
        self.controller.refresh_followup_state()
        self.assertIs(self.ui.followupsEnabledBox.currentData(), True, "Keep an unsaved switch edit")
        self.ui.saveCompanionButton.click()
        self.assertTrue(self.followup_repository.enabled())
        self.assertTrue(self.manager.followups_enabled)

    def test_busy_save_and_restore_are_disabled_and_guarded(self):
        original = self.path.read_bytes()
        self.controller.set_busy(True)
        self.ui.recentMessagesEdit.setText("6")
        self.assertFalse(self.ui.saveCompanionButton.isEnabled())
        self.assertFalse(self.ui.recoveryCompanionButton.isEnabled())
        self.controller.save()
        self.controller.restore_defaults()
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.ui.recentMessagesEdit.text(), "6")
        self.controller.set_busy(False)
        self.assertTrue(self.ui.saveCompanionButton.isEnabled())

    def test_model_page_shows_save_clear_validation_and_write_results(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.settingTab)
        self.ui.provider_Edit.setText("test")
        self.ui.apiKeyEdit.setText("fake-key")
        self.ui.baseUrlEdit.setText("https://example.invalid")
        self.ui.modelEdit.setText("test-model")
        self.ui.LLMSaveButton.click()
        self.assertEqual(self.ui.llmStatusLabel.text(), "模型配置已保存。")
        saved = (self.root / ".env").read_bytes()
        self.ui.LLMCleanButton.click()
        self.assertIn("未修改", self.ui.llmStatusLabel.text())
        self.assertEqual((self.root / ".env").read_bytes(), saved)
        with patch("app.main_window_controller.QMessageBox.warning"):
            self.ui.LLMSaveButton.click()
        self.assertIn("请填写", self.ui.llmStatusLabel.text())
        self.assertEqual((self.root / ".env").read_bytes(), saved)
        with patch.object(self.main_controller._settings_repository, "save", side_effect=PermissionError("locked")):
            with patch("app.main_window_controller.QMessageBox.critical"):
                self.ui.LLMSaveButton.click()
        self.assertIn("保存模型配置失败", self.ui.llmStatusLabel.text())
        self.assertEqual(self.ui.statusLabel.text(), self.ui.llmStatusLabel.text())
        self.assertEqual((self.root / ".env").read_bytes(), saved)

    def test_file_write_failure_keeps_old_policy_and_cleans_temp_file(self):
        original = self.path.read_bytes()
        self.fill(replace(CompanionPolicy(), recent_messages=6))
        with patch("storage.companion_policy_repository.os.replace", side_effect=PermissionError("locked")):
            with patch("app.companion_settings_controller.QMessageBox.warning"):
                self.ui.saveCompanionButton.click()
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.manager.policy, CompanionPolicy())
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_preference_write_failure_restores_file_policy(self):
        self.fill(replace(CompanionPolicy(), recent_messages=6, followups_enabled=False))
        with patch.object(self.followup_repository, "set_enabled", side_effect=sqlite3.OperationalError("locked")):
            with patch("app.companion_settings_controller.QMessageBox.warning"):
                self.ui.saveCompanionButton.click()
        self.assertEqual(self.policy_repository.load(), CompanionPolicy())
        self.assertEqual(self.manager.policy, CompanionPolicy())
        self.assertTrue(self.manager.followups_enabled)


if __name__ == "__main__":
    unittest.main()
