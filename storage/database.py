"""SQLite database initialization."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3


class Database:
    """Create SQLite connections and initialize the application's schema."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def connection(self):
        """Yield one transaction and always close its SQLite file handle."""
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        if self.database_path.is_file():
            with self.connection() as connection:
                old_schema = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'messages'"
                ).fetchone()
                upgraded = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'summaries'"
                ).fetchone()
                backup_path = self.database_path.with_name(self.database_path.stem + '.pre-continuity.db')
                if old_schema and not upgraded and not backup_path.exists():
                    backup = sqlite3.connect(backup_path)
                    try:
                        connection.backup(backup)
                    finally:
                        backup.close()
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                ON messages(conversation_id, id);
                CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at, id);

                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_memories_importance_created
                ON memories(importance DESC, id DESC);

                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                    start_message_id INTEGER NOT NULL REFERENCES messages(id),
                    end_message_id INTEGER NOT NULL REFERENCES messages(id),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(conversation_id, end_message_id)
                );
                CREATE INDEX IF NOT EXISTS idx_summaries_conversation
                ON summaries(conversation_id, end_message_id DESC);

                CREATE TABLE IF NOT EXISTS followups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL UNIQUE,
                    kind TEXT NOT NULL,
                    source_message_id INTEGER NOT NULL REFERENCES messages(id),
                    due_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'dismissed')),
                    last_asked_at TEXT,
                    last_question_message_id INTEGER REFERENCES messages(id),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_followups_due ON followups(status, due_at);
                CREATE INDEX IF NOT EXISTS idx_followups_asked ON followups(last_asked_at DESC);
                CREATE TABLE IF NOT EXISTS companion_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
