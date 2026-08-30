"""Value object and validation for LLM connection settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMSettings:
    provider: str = ""
    api_key: str = ""
    base_url: str = ""
    model: str = ""

    def missing_fields(self) -> list[str]:
        """Return the required environment-variable names that have no value."""
        values = {
            "LLM_PROVIDER": self.provider,
            "LLM_API_KEY": self.api_key,
            "LLM_BASE_URL": self.base_url,
            "LLM_MODEL": self.model,
        }
        return [name for name, value in values.items() if not value.strip()]

    def validate(self) -> None:
        """Raise ValueError when a required setting is blank or malformed."""
        missing = self.missing_fields()
        if missing:
            raise ValueError(f"请填写：{', '.join(missing)}")

        if any("\n" in value or "\r" in value for value in self.values()):
            raise ValueError("模型配置不能包含换行符。")

    def values(self) -> tuple[str, str, str, str]:
        return self.provider, self.api_key, self.base_url, self.model
