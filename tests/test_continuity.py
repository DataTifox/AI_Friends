"""Offline regression coverage for persistence, bounded history and follow-ups."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import json
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMainWindow

from app.main_window_controller import MainWindowController
from core.companion_policy import CompanionPolicy
from core.conversation import ConversationManager
from core.followup import FollowupManager
from core.llm_settings import LLMSettings
from core.memory import MemoryManager
from core.personality import PersonalityManager
from core.summary import SummaryManager
from core.time_utils import db_time, display_time
from services.llm.base import LLMRequestError
from storage.database import Database
from storage.followup_repository import FollowupRepository
from storage.repository import ConversationRepository, MemoryRepository
from storage.settings_repository import SettingsRepository
from storage.summary_repository import SummaryRepository
from ui.generated.main_window import Ui_MainWindow
from tools.export_messages import export_day

PROJECT = Path(__file__).resolve().parents[1]


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.fail_summary = False

    def chat(self, messages):
        self.calls.append(messages)
        if messages[0]["content"].startswith("请压缩"):
            if self.fail_summary:
                raise LLMRequestError("simulated summary error")
            return "用户之前买了笛子，但没有说已经开始学习。"
        return "那支笛子最近有试着吹吗？"


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.database = Database(self.root / "companion.db")
        self.database.initialize()
        self.messages = ConversationRepository(self.database)
        self.conversation = self.messages.create_conversation("test")
        self.summary_repository = SummaryRepository(self.database)
        self.followup_repository = FollowupRepository(self.database)
        self.settings = SettingsRepository(self.root / ".env")
        self.settings.save(LLMSettings("test", "fake-key", "https://example.invalid", "test"))
        self.policy = CompanionPolicy()
        self.now = datetime(2026, 10, 12, 4, tzinfo=timezone.utc)
        self.provider = FakeProvider()
        self.followups = FollowupManager(self.followup_repository, self.policy, lambda: self.now)
        self.summaries = SummaryManager(self.messages, self.summary_repository, self.policy, lambda: self.now)
        self.manager = ConversationManager(
            self.messages, self.settings, PersonalityManager(PROJECT / "config/personality.json"),
            MemoryManager(MemoryRepository(self.database)), lambda settings: self.provider,
            self.summaries, self.followups, self.policy,
        )

    def tearDown(self):
        self.directory.cleanup()

    def seed(self, count):
        with self.database.connection() as connection:
            connection.executemany(
                """INSERT INTO messages(conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)""",
                [(self.conversation.id, "user" if index % 2 == 0 else "assistant",
                  f"message-{index}", db_time(self.now)) for index in range(count)],
            )

    def observe(self, text):
        message = self.manager.record_user_message(self.conversation.id, text)
        with self.database.connection() as connection:
            connection.execute("UPDATE messages SET created_at = ? WHERE id = ?", (db_time(self.now), message.id))
        return message

    def test_pages_and_indexed_recent_query(self):
        self.seed(5000)
        latest = self.messages.message_page(self.conversation.id, 50)
        previous = self.messages.message_page(self.conversation.id, 50, latest[0].id)
        self.assertEqual(latest[-1].content, "message-4999")
        self.assertEqual(previous[-1].content, "message-4949")
        self.assertFalse({item.id for item in latest} & {item.id for item in previous})
        with self.database.connection() as connection:
            plan = connection.execute(
                "EXPLAIN QUERY PLAN SELECT * FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 12",
                (self.conversation.id,),
            ).fetchall()
        self.assertTrue(any("idx_messages_conversation_created" in row["detail"] for row in plan))
        with patch.object(self.messages, "list_messages", side_effect=AssertionError("full scan")):
            self.manager.record_user_message(self.conversation.id, "hello")
            self.manager.reply_to_user_message(self.conversation.id)
        self.assertLessEqual(len(self.provider.calls[0]), 13)

    def test_summary_ranges_increment_without_deleting_messages(self):
        self.seed(60)
        self.assertTrue(self.summaries.update(self.conversation.id, self.provider))
        self.assertTrue(self.summaries.update(self.conversation.id, self.provider))
        self.assertFalse(self.summaries.update(self.conversation.id, self.provider))
        with self.database.connection() as connection:
            ranges = connection.execute("SELECT start_message_id, end_message_id FROM summaries ORDER BY id").fetchall()
            count = connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        self.assertEqual([(row[0], row[1]) for row in ranges], [(1, 24), (25, 48)])
        self.assertEqual(count, 60)
        context = self.manager._build_context(self.conversation.id)
        self.assertIn("买了笛子", context[0]["content"])

    def test_summary_failure_keeps_reply_and_retries_same_range(self):
        self.seed(40)
        self.provider.fail_summary = True
        self.observe("hello")
        with self.assertLogs("core.conversation", level="WARNING"):
            reply = self.manager.reply_to_user_message(self.conversation.id)
        self.assertEqual(reply.role, "assistant")
        self.assertEqual(self.summary_repository.recent(self.conversation.id, 3), [])
        self.provider.fail_summary = False
        self.assertTrue(self.summaries.update(self.conversation.id, self.provider))

    def test_previous_day_small_batch_and_china_timestamp(self):
        self.seed(16)
        with self.database.connection() as connection:
            connection.execute("UPDATE messages SET created_at = '2026-10-10 18:00:00' WHERE id <= 4")
        self.assertTrue(self.summaries.update(self.conversation.id, self.provider))
        self.assertEqual(display_time("2026-10-11 18:00:00"), "2026-10-12 02:00")

    def test_context_character_budget(self):
        self.observe("x" * 50000)
        context = self.manager._build_context(self.conversation.id)
        self.assertLessEqual(sum(len(item["content"]) for item in context), self.policy.context_max_chars)
        self.assertTrue(self.messages.message_page(self.conversation.id)[0].content.endswith("x" * 50000))

    def test_purchase_followup_persists_and_does_not_assume_learning(self):
        self.observe("我今天买了一支笛子。")
        self.assertFalse(self.manager.has_due_followup())
        self.now += timedelta(days=3)
        question = self.manager.proactive_message(self.conversation.id)
        self.assertIsNotNone(question)
        self.assertIn("不假定正在学习", self.provider.calls[-1][-1]["content"])
        restarted = FollowupManager(FollowupRepository(self.database), self.policy, lambda: self.now)
        self.assertIsNone(restarted.due())
        self.assertIsNone(self.manager.proactive_message(self.conversation.id))

    def test_global_daily_limit_across_topics(self):
        self.observe("我买了笛子。")
        self.observe("我准备学习吉他。")
        self.now += timedelta(days=3)
        self.assertIsNotNone(self.manager.proactive_message(self.conversation.id))
        self.assertFalse(self.manager.has_due_followup())
        self.now += timedelta(days=1)
        self.assertTrue(self.manager.has_due_followup())

    def test_refusal_stops_topic_without_disabling_other_topics(self):
        self.observe("我买了笛子。")
        self.observe("我准备学习吉他。")
        self.observe("别再问笛子了。")
        self.now += timedelta(days=3)
        self.assertEqual(self.followups.due().topic, "吉他")
        self.assertTrue(self.followup_repository.enabled())

    def test_global_opt_out_survives_restart_and_can_be_enabled(self):
        self.observe("我买了笛子。")
        self.observe("以后不要主动问我了。")
        self.now += timedelta(days=3)
        self.assertIsNone(FollowupManager(FollowupRepository(self.database), self.policy, lambda: self.now).due())
        self.observe("开启主动关心。")
        self.assertTrue(self.manager.has_due_followup())

    def test_hypothetical_and_negative_are_not_events(self):
        for text in ("比如我买了笛子。", "如果我买了笛子会怎样？", "我没有买笛子。", "朋友买了笛子。"):
            self.observe(text)
        self.now += timedelta(days=3)
        self.assertFalse(self.manager.has_due_followup())

    def test_recent_progress_defers_and_quiet_hours_suppress(self):
        self.observe("我买了笛子。")
        self.now += timedelta(days=3)
        self.observe("笛子昨天试着吹了一下。")
        self.assertFalse(self.manager.has_due_followup())
        self.now += timedelta(days=7)
        self.assertTrue(self.manager.has_due_followup())
        self.now = self.now.replace(hour=16)  # midnight China time
        self.assertFalse(self.manager.has_due_followup())

    def test_failed_followup_does_not_consume_schedule(self):
        self.observe("我买了笛子。")
        self.now += timedelta(days=3)
        with patch.object(self.provider, "chat", side_effect=LLMRequestError("offline")):
            with self.assertRaises(LLMRequestError):
                self.manager.proactive_message(self.conversation.id)
        self.assertTrue(self.manager.has_due_followup())
        self.assertEqual(len(self.messages.message_page(self.conversation.id)), 1)

    def test_existing_database_upgrade_preserves_data_and_creates_backup(self):
        legacy_path = self.root / "legacy.db"
        connection = sqlite3.connect(legacy_path)
        connection.executescript("""
            CREATE TABLE conversations(id INTEGER PRIMARY KEY, title TEXT, created_at TEXT, updated_at TEXT);
            CREATE TABLE messages(id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT, created_at TEXT);
            CREATE TABLE memories(id INTEGER PRIMARY KEY, content TEXT, importance INTEGER, created_at TEXT);
            INSERT INTO conversations VALUES(1, 'original', '2026-01-01 00:00:00', '2026-01-01 00:00:00');
            INSERT INTO messages VALUES(1, 1, 'user', 'original message', '2026-01-01 00:00:00');
        """)
        connection.close()
        upgraded = Database(legacy_path)
        upgraded.initialize()
        upgraded.initialize()
        self.assertEqual(ConversationRepository(upgraded).message_page(1)[0].content, "original message")
        backup = sqlite3.connect(self.root / "legacy.pre-continuity.db")
        try:
            self.assertEqual(backup.execute("SELECT content FROM messages").fetchone()[0], "original message")
            self.assertIsNone(backup.execute("SELECT 1 FROM sqlite_master WHERE name='summaries'").fetchone())
        finally:
            backup.close()

    def test_export_uses_china_calendar_day_boundaries(self):
        self.seed(4)
        with self.database.connection() as connection:
            dates = ["2026-10-11 15:59:59", "2026-10-11 16:00:00",
                     "2026-10-12 15:59:59", "2026-10-12 16:00:00"]
            for index, value in enumerate(dates, 1):
                connection.execute("UPDATE messages SET created_at = ? WHERE id = ?", (value, index))
        output = self.root / "day.jsonl"
        self.assertEqual(export_day(self.database.database_path, output, "2026-10-12"), 2)
        records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([item["id"] for item in records], [2, 3])
        self.assertTrue(records[0]["local_time"].endswith("+08:00"))
        self.assertEqual(len(self.messages.list_messages(self.conversation.id)), 4)


    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_nonblocking_send_guard_and_history_pagination(self):
        self.seed(100)
        self.policy = replace(self.policy, followups_enabled=False)
        self.manager.policy = self.policy
        window = QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(window)
        controller = MainWindowController(window, ui, self.settings, self.manager)
        controller._followup_timer.stop()
        self.assertEqual(len(controller._visible_messages), 50)
        controller.load_older_messages()
        self.assertEqual(len(controller._visible_messages), 100)
        gate = threading.Event()
        original = self.provider.chat

        def blocked(messages):
            gate.wait(3)
            return original(messages)

        ticked = []
        with patch.object(self.provider, "chat", side_effect=blocked):
            ui.inputWindow.setPlainText("hello from UI")
            ui.sendButton.click()
            controller.send_user_message()
            self.assertTrue(controller._busy)
            QTimer.singleShot(0, lambda: ticked.append(True))
            QTest.qWait(30)
            self.assertTrue(ticked, "UI event loop should continue while request is blocked")
            gate.set()
            deadline = time.monotonic() + 5
            while controller._busy and time.monotonic() < deadline:
                QTest.qWait(10)
        self.assertFalse(controller._busy)
        self.assertTrue(ui.sendButton.isEnabled())
        self.assertEqual(sum(message.content == "hello from UI" for message in self.messages.list_messages(self.conversation.id)), 1)
        self.assertIn("hello from UI", ui.showWindow.toPlainText())
        self.assertIn("那支笛子", ui.showWindow.toPlainText())
        QThreadPool.globalInstance().waitForDone(5000)
        window.close()

    def test_controller_followup_respects_typing_tabs_and_idle(self):
        self.observe("我今天买了笛子。")
        self.now += timedelta(days=3)
        window = QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(window)
        controller = MainWindowController(window, ui, self.settings, self.manager)
        controller._followup_timer.stop()
        with patch.object(window, "isActiveWindow", return_value=True):
            controller.check_followup()
            self.assertFalse(controller._busy, "Opening alone should not immediately interrupt")
            ui.inputWindow.setPlainText("still typing")
            controller._last_activity = time.monotonic() - 121
            controller.check_followup()
            self.assertFalse(controller._busy)
            ui.inputWindow.clear()
            ui.tabWidget.setCurrentWidget(ui.settingTab)
            controller._last_activity = time.monotonic() - 121
            controller.check_followup()
            self.assertFalse(controller._busy)
            ui.tabWidget.setCurrentWidget(ui.dialogueTab)
            controller._last_activity = time.monotonic() - 121
            controller.check_followup()
            self.assertTrue(controller._busy)
            deadline = time.monotonic() + 5
            while controller._busy and time.monotonic() < deadline:
                QTest.qWait(10)
            self.assertFalse(controller._busy)
        self.assertIn("那支笛子", ui.showWindow.toPlainText())
        self.assertFalse(self.manager.has_due_followup())
        QThreadPool.globalInstance().waitForDone(5000)
        window.close()


if __name__ == "__main__":
    unittest.main()
