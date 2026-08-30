"""Personality loading and system-prompt construction."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Personality:
    name: str
    personality: str
    speaking_style: str


class PersonalityManager:
    """Load the companion personality and turn it into a system prompt."""

    def __init__(self, personality_path: Path) -> None:
        self._personality_path = personality_path
        self._personality = self._load()

    @property
    def name(self) -> str:
        return self._personality.name

    def build_system_prompt(self, memories: list[str]) -> str:
        prompt = (
            f"你是 {self._personality.name}，一个 AI 聊天陪伴机器人。\n"
            f"人格：{self._personality.personality}\n"
            f"表达风格：{self._personality.speaking_style}\n"
            "请自然地陪伴用户聊天，不要自称客服，不要编造自己记得的事情。"
        )
        if memories:
            prompt += "\n\n已知的用户长期信息（仅在相关时自然使用）：\n" + "\n".join(
                f"- {memory}" for memory in memories
            )
        return prompt

    def _load(self) -> Personality:
        try:
            raw_data = json.loads(self._personality_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"无法加载人格配置：{error}") from error

        fields = ("name", "personality", "speaking_style")
        if not isinstance(raw_data, dict) or any(
            not isinstance(raw_data.get(field), str) or not raw_data[field].strip()
            for field in fields
        ):
            raise ValueError("人格配置必须包含非空的 name、personality、speaking_style。")

        return Personality(**{field: raw_data[field].strip() for field in fields})
