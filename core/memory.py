"""Rule-based long-term memory extraction and retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import re

from storage.repository import Memory, MemoryRepository


@dataclass(frozen=True)
class MemoryCandidate:
    content: str
    importance: int


class MemoryManager:
    """Store a small, useful subset of user statements as long-term memories."""

    _RULES: tuple[tuple[re.Pattern[str], str, int], ...] = (
        (re.compile(r"我(?:很)?喜欢(?P<value>[^。！？\n]{1,60})"), "用户喜欢{value}", 2),
        (re.compile(r"我最近(?:正在|在)?学(?:习)?(?P<value>[^。！？\n]{1,60})"), "用户最近在学{value}", 2),
        (re.compile(r"我(?:正)?准备(?P<value>[^。！？\n]{1,60})"), "用户准备{value}", 2),
        (re.compile(r"我的名字是(?P<value>[^。！？\n]{1,30})"), "用户的名字是{value}", 3),
    )

    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    def relevant_memories(self, limit: int = 5) -> list[str]:
        return [memory.content for memory in self._repository.list_for_context(limit)]

    def extract_and_store(self, user_content: str) -> list[Memory]:
        """Extract at most one durable fact per user message using local rules."""
        candidate = self._extract_candidate(user_content)
        if candidate is None or self._repository.exists(candidate.content):
            return []
        return [self._repository.add(candidate.content, candidate.importance)]

    def _extract_candidate(self, user_content: str) -> MemoryCandidate | None:
        for pattern, template, importance in self._RULES:
            match = pattern.search(user_content)
            if match:
                value = match.group("value").strip(" ，,。！？")
                if value:
                    return MemoryCandidate(template.format(value=value), importance)
        return None
