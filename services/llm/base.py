"""Language-model provider interface and domain-specific errors."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMError(RuntimeError):
    """Base exception for a model request that cannot produce a reply."""


class LLMConfigurationError(LLMError):
    """The configured model connection is incomplete or invalid."""


class LLMRequestError(LLMError):
    """The remote model service could not complete the request."""


class LLMProvider(ABC):
    """Interface used by ConversationManager, independent of model vendors."""

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Return one assistant reply for OpenAI-format chat messages."""
