"""Persist incremental summaries with references to their original messages."""

from storage.database import Database


class SummaryRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def recent(self, conversation_id: int, limit: int) -> list[str]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """SELECT content FROM summaries WHERE conversation_id = ?
                ORDER BY end_message_id DESC LIMIT ?""", (conversation_id, limit),
            ).fetchall()
        return [row["content"] for row in reversed(rows)]

    def add(self, conversation_id: int, start_id: int, end_id: int, content: str) -> None:
        with self._database.connection() as connection:
            connection.execute(
                """INSERT OR IGNORE INTO summaries
                (conversation_id, start_message_id, end_message_id, content)
                VALUES (?, ?, ?, ?)""", (conversation_id, start_id, end_id, content),
            )
