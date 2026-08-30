"""Repositories for conversations and messages."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from storage.database import Database


@dataclass(frozen=True)
class Conversation:
    id: int
    title: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str


@dataclass(frozen=True)
class Memory:
    id: int
    content: str
    importance: int
    created_at: str


class ConversationRepository:
    """Persist and retrieve conversations and their ordered messages."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def get_latest_conversation(self) -> Conversation | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """
            ).fetchone()
        return self._conversation_from_row(row) if row else None

    def create_conversation(self, title: str) -> Conversation:
        with self._database.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO conversations (title) VALUES (?)",
                (title,),
            )
            row = connection.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._conversation_from_row(row)

    def list_messages(self, conversation_id: int) -> list[Message]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()
        return [self._message_from_row(row) for row in rows]

    def add_message(self, conversation_id: int, role: str, content: str) -> Message:
        if role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported message role: {role}")
        if not content.strip():
            raise ValueError("Message content cannot be empty.")

        with self._database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
                """,
                (conversation_id, role, content),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )
            row = connection.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM messages WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._message_from_row(row)

    @staticmethod
    def _conversation_from_row(row: sqlite3.Row) -> Conversation:
        return Conversation(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _message_from_row(row: sqlite3.Row) -> Message:
        return Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )


class MemoryRepository:
    """Persist a small set of stable user facts for future chat context."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def list_for_context(self, limit: int) -> list[Memory]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT id, content, importance, created_at
                FROM memories
                ORDER BY importance DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._memory_from_row(row) for row in rows]

    def exists(self, content: str) -> bool:
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM memories WHERE content = ? LIMIT 1",
                (content,),
            ).fetchone()
        return row is not None

    def add(self, content: str, importance: int) -> Memory:
        if not content.strip():
            raise ValueError("Memory content cannot be empty.")
        with self._database.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO memories (content, importance) VALUES (?, ?)",
                (content.strip(), importance),
            )
            row = connection.execute(
                """
                SELECT id, content, importance, created_at
                FROM memories WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._memory_from_row(row)

    @staticmethod
    def _memory_from_row(row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            created_at=row["created_at"],
        )
