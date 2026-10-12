"""Configurable limits for context, summaries and proactive conversation."""

from dataclasses import dataclass, fields
import json
from pathlib import Path


@dataclass(frozen=True)
class CompanionPolicy:
    recent_messages: int = 12
    history_page_size: int = 50
    summary_batch_size: int = 24
    summary_count: int = 3
    summary_max_chars: int = 800
    context_max_chars: int = 16000
    followups_enabled: bool = True
    followup_delay_days: int = 3
    followup_cooldown_days: int = 7
    followup_expiry_days: int = 30
    followup_idle_seconds: int = 120
    quiet_start_hour: int = 22
    quiet_end_hour: int = 9

    @classmethod
    def load(cls, path: Path) -> "CompanionPolicy":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("陪伴策略配置必须为 JSON 对象。")
        # Keep explanatory metadata in standard JSON without changing policy values.
        comments = raw.pop("_comments", None)
        if comments is not None and (
            not isinstance(comments, dict)
            or any(not isinstance(value, str) for value in comments.values())
        ):
            raise ValueError("_comments 必须为包含文字说明的 JSON 对象。")
        if set(raw) - {field.name for field in fields(cls)}:
            raise ValueError("陪伴策略配置包含未知字段或格式错误。")
        policy = cls(**raw)
        policy.validate()
        return policy

    def validate(self) -> None:
        """Use the same validation for file loading and interactive edits."""
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name == "followups_enabled":
                if not isinstance(value, bool):
                    raise ValueError("followups_enabled 必须为布尔值。")
            elif type(value) is not int or value < 0:
                raise ValueError(f"{field.name} 必须为非负整数。")
        if any(getattr(self, name) < 1 for name in (
            "recent_messages", "history_page_size", "summary_count", "summary_max_chars",
            "followup_delay_days", "followup_cooldown_days", "followup_expiry_days",
        )) or self.summary_batch_size < 2 or self.context_max_chars < 2000:
            raise ValueError("数量和天数必须为正数，摘要批次至少 2 条，上下文限制至少 2000 字符。")
        if self.quiet_start_hour > 23 or self.quiet_end_hour > 23:
            raise ValueError("静默时间必须在 0 至 23 之间。")
