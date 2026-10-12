"""Persistent follow-up schedule, cooldown, dismissal and atomic questions."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import re

from core.time_utils import db_time
from storage.database import Database
from storage.repository import ConversationRepository, Message


@dataclass(frozen=True)
class Followup:
    id: int
    topic: str
    kind: str
    source_message_id: int
    source_content: str
    due_at: str


class FollowupRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def enabled(self) -> bool:
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT value FROM companion_preferences WHERE key = 'followups_enabled'"
            ).fetchone()
        return row is None or row["value"] == "1"

    def set_enabled(self, enabled: bool) -> None:
        with self._database.connection() as connection:
            connection.execute(
                """INSERT INTO companion_preferences(key, value) VALUES ('followups_enabled', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
                ("1" if enabled else "0",),
            )

    def create(self, topic: str, kind: str, message_id: int, due: datetime) -> None:
        with self._database.connection() as connection:
            connection.execute(
                """INSERT INTO followups(topic, kind, source_message_id, due_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(topic) DO UPDATE SET source_message_id = excluded.source_message_id,
                    kind = excluded.kind WHERE followups.status = 'active'""",
                (topic, kind, message_id, db_time(due)),
            )

    def update_from_user(self, message: Message, now: datetime, cooldown_days: int) -> None:
        cancel_words = ("不学了", "不练了", "放弃", "别问", "不要问", "不想聊", "别提", "不想学")
        cancelling = any(word in message.content for word in cancel_words) or bool(re.search(
            r"不(?:学|练|玩).{0,24}了|(?:别|不要).{0,8}问", message.content
        ))
        with self._database.connection() as connection:
            matches = connection.execute(
                "SELECT id FROM followups WHERE status = 'active' AND instr(?, topic) > 0",
                (message.content,),
            ).fetchall()
            if not matches:
                latest = connection.execute(
                    """SELECT f.id FROM followups f JOIN messages m ON m.id = f.last_question_message_id
                    WHERE f.status = 'active' AND f.last_asked_at >= ? AND m.conversation_id = ?
                    AND NOT EXISTS (SELECT 1 FROM messages newer WHERE newer.conversation_id = ?
                        AND newer.id > f.last_question_message_id AND newer.id < ?)
                    ORDER BY f.last_asked_at DESC LIMIT 1""",
                    (db_time(now - timedelta(days=1)), message.conversation_id,
                     message.conversation_id, message.id),
                ).fetchone()
                matches = [latest] if latest else []
            for row in matches:
                if cancelling:
                    connection.execute("UPDATE followups SET status = 'dismissed' WHERE id = ?",
                                       (row["id"],))
                else:
                    connection.execute("UPDATE followups SET due_at = ? WHERE id = ?",
                                       (db_time(now + timedelta(days=cooldown_days)), row["id"]))

    def due(self, now: datetime, expiry_days: int) -> Followup | None:
        if not self.enabled():
            return None
        with self._database.connection() as connection:
            asked = connection.execute(
                "SELECT last_asked_at FROM followups ORDER BY last_asked_at DESC LIMIT 1"
            ).fetchone()
            if asked and asked["last_asked_at"] and asked["last_asked_at"] > db_time(now - timedelta(days=1)):
                return None
            row = connection.execute(
                """SELECT f.*, m.content AS source_content FROM followups f
                JOIN messages m ON m.id = f.source_message_id
                WHERE f.status = 'active' AND f.due_at <= ? AND m.created_at >= ?
                ORDER BY f.due_at, f.id LIMIT 1""",
                (db_time(now), db_time(now - timedelta(days=expiry_days))),
            ).fetchone()
        return Followup(**{name: row[name] for name in Followup.__dataclass_fields__}) if row else None

    def record_question(self, conversation_id: int, item: Followup, content: str,
                        now: datetime, cooldown_days: int) -> Message | None:
        """Question persistence and its cooldown are one atomic transaction."""
        if not content.strip():
            raise ValueError("主动关心回复为空。")
        with self._database.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            state = connection.execute(
                "SELECT status, due_at FROM followups WHERE id = ?", (item.id,),
            ).fetchone()
            enabled = connection.execute(
                "SELECT value FROM companion_preferences WHERE key = 'followups_enabled'"
            ).fetchone()
            recent = connection.execute(
                "SELECT 1 FROM followups WHERE last_asked_at > ? LIMIT 1",
                (db_time(now - timedelta(days=1)),),
            ).fetchone()
            if (not state or state["status"] != "active" or state["due_at"] > db_time(now)
                    or (enabled and enabled["value"] == "0") or recent):
                return None
            cursor = connection.execute(
                "INSERT INTO messages(conversation_id, role, content) VALUES (?, 'assistant', ?)",
                (conversation_id, content),
            )
            connection.execute(
                """UPDATE followups SET last_asked_at = ?, last_question_message_id = ?,
                due_at = ? WHERE id = ?""",
                (db_time(now), cursor.lastrowid,
                 db_time(now + timedelta(days=cooldown_days)), item.id),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )
            row = connection.execute("SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return ConversationRepository._message_from_row(row)
