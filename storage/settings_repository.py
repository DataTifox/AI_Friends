"""Persistence for local LLM settings stored in the project .env file."""

from __future__ import annotations

from pathlib import Path

from core.llm_settings import LLMSettings


SETTINGS_KEYS = {
    "LLM_PROVIDER": "provider",
    "LLM_API_KEY": "api_key",
    "LLM_BASE_URL": "base_url",
    "LLM_MODEL": "model",
}


class SettingsRepository:
    """Read and update only this application's LLM variables in a .env file."""

    def __init__(self, env_path: Path) -> None:
        self._env_path = env_path

    def load(self) -> LLMSettings:
        values = {attribute: "" for attribute in SETTINGS_KEYS.values()}
        if not self._env_path.is_file():
            return LLMSettings(**values)

        for line in self._env_path.read_text(encoding="utf-8").splitlines():
            key, separator, raw_value = line.partition("=")
            if not separator or key.strip() not in SETTINGS_KEYS:
                continue
            values[SETTINGS_KEYS[key.strip()]] = self._decode_value(raw_value.strip())

        return LLMSettings(**values)

    def save(self, settings: LLMSettings) -> None:
        """Update LLM variables while preserving unrelated .env lines and comments."""
        settings.validate()
        current_lines = []
        if self._env_path.is_file():
            current_lines = self._env_path.read_text(encoding="utf-8").splitlines()

        output_lines: list[str] = []
        written_keys: set[str] = set()
        values = self._as_env_values(settings)

        for line in current_lines:
            key, separator, _ = line.partition("=")
            normalized_key = key.strip()
            if separator and normalized_key in SETTINGS_KEYS:
                output_lines.append(f"{normalized_key}={values[normalized_key]}")
                written_keys.add(normalized_key)
            else:
                output_lines.append(line)

        for key in SETTINGS_KEYS:
            if key not in written_keys:
                output_lines.append(f"{key}={values[key]}")

        self._env_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")

    @staticmethod
    def _decode_value(value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
        return value

    @staticmethod
    def _as_env_values(settings: LLMSettings) -> dict[str, str]:
        return {
            "LLM_PROVIDER": settings.provider.strip(),
            "LLM_API_KEY": settings.api_key.strip(),
            "LLM_BASE_URL": settings.base_url.strip(),
            "LLM_MODEL": settings.model.strip(),
        }
