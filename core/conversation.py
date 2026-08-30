"""Conversation orchestration, context assembly, model calls and persistence."""

from __future__ import annotations

from collections.abc import Callable

from core.llm_settings import LLMSettings
from core.memory import MemoryManager
from core.personality import PersonalityManager
from services.llm.base import LLMProvider
from storage.repository import Conversation, ConversationRepository, Message
from storage.settings_repository import SettingsRepository


class ConversationManager:
    """Own the active conversation and coordinate all non-UI chat work."""

    MAX_RECENT_MESSAGES = 12

    def __init__(
        self,
        repository: ConversationRepository,
        settings_repository: SettingsRepository,
        personality_manager: PersonalityManager,
        memory_manager: MemoryManager,
        provider_factory: Callable[[LLMSettings], LLMProvider],
    ) -> None:
        self._repository = repository
        self._settings_repository = settings_repository
        self._personality_manager = personality_manager
        self._memory_manager = memory_manager
        self._provider_factory = provider_factory

    @property
    def assistant_name(self) -> str:
        return self._personality_manager.name

    def open_recent_or_create(self) -> Conversation:
        """Return the latest conversation, creating an empty one when needed."""
        return self._repository.get_latest_conversation() or self._repository.create_conversation(
            "新对话"
        )

    def load_messages(self, conversation_id: int) -> list[Message]:
        return self._repository.list_messages(conversation_id)

    def record_user_message(self, conversation_id: int, content: str) -> Message:
        """Persist one user message before requesting a model reply."""
        return self._repository.add_message(conversation_id, "user", content.strip())

    def reply_to_user_message(self, conversation_id: int) -> Message:
        """Build context, request a reply, persist it, then update long-term memory."""
        provider = self._provider_factory(self._settings_repository.load())
        response_content = provider.chat(self._build_context(conversation_id))
        assistant_message = self._repository.add_message(
            conversation_id, "assistant", response_content
        )

        user_messages = [
            message
            for message in reversed(self._repository.list_messages(conversation_id))
            if message.role == "user"
        ]
        if user_messages:
            try:
                self._memory_manager.extract_and_store(user_messages[0].content)
            except (OSError, ValueError):
                # Memory is an enhancement; a storage failure must not discard a reply.
                pass
        return assistant_message

    def _build_context(self, conversation_id: int) -> list[dict[str, str]]:
        memories = self._memory_manager.relevant_memories()
        recent_messages = self._repository.list_messages(conversation_id)[
            -self.MAX_RECENT_MESSAGES :
        ]
        return [
            {
                "role": "system",
                "content": self._personality_manager.build_system_prompt(memories),
            },
            *[
                {"role": message.role, "content": message.content}
                for message in recent_messages
            ],
        ]
