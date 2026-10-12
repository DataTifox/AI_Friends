"""Conservative local extraction of experiences worth following up on."""

from datetime import timedelta
import re

from core.companion_policy import CompanionPolicy
from core.time_utils import CHINA_TIME, utc_now
from storage.followup_repository import Followup, FollowupRepository
from storage.repository import Message


class FollowupManager:
    _PATTERNS = (
        ("learning", re.compile(
            r"^我(?:最近|今天|现在)?(?:开始|正在|准备|打算|在)(?:学习|学|练习)(?P<topic>[^，,。！？\n]{1,24})"
        )),
        ("purchase", re.compile(
            r"^我(?:今天|昨天|刚刚|刚|最近)?买了(?:一[支把台本个套])?(?P<topic>[^，,。！？\n]{1,24})"
        )),
    )

    def __init__(self, repository: FollowupRepository, policy: CompanionPolicy, clock=utc_now) -> None:
        self._repository = repository
        self._policy = policy
        self._clock = clock

    def observe(self, message: Message) -> None:
        now = self._clock()
        if any(phrase in message.content for phrase in (
            "不要主动问我", "别主动问我", "不要主动问了", "别主动问了", "关闭主动关心",
        )):
            self._repository.set_enabled(False)
            return
        if any(phrase in message.content for phrase in ("开启主动关心", "可以主动问我")):
            self._repository.set_enabled(True)
        self._repository.update_from_user(message, now, self._policy.followup_cooldown_days)
        if not self._policy.followups_enabled or not self._repository.enabled():
            return
        for sentence in re.split(r"[。！？\n]", message.content):
            sentence = sentence.strip()
            if any(word in sentence for word in ("如果", "假如", "比如", "例如", "别问", "不要问", "不想学")):
                continue
            for kind, pattern in self._PATTERNS:
                match = pattern.match(sentence)
                if match:
                    topic = re.split(r"准备|打算|计划", match["topic"])[0].strip(" ，,")
                    if topic:
                        self._repository.create(topic, kind, message.id,
                                                now + timedelta(days=self._policy.followup_delay_days))
                    return

    @property
    def enabled(self) -> bool:
        return self._policy.followups_enabled and self._repository.enabled()

    def apply_policy(self, policy: CompanionPolicy) -> None:
        # An explicit UI save reconciles the file switch with the chat preference.
        self._repository.set_enabled(policy.followups_enabled)
        self._policy = policy

    def due(self) -> Followup | None:
        if not self._policy.followups_enabled:
            return None
        hour = self._clock().astimezone(CHINA_TIME).hour
        start, end = self._policy.quiet_start_hour, self._policy.quiet_end_hour
        quiet = (start <= hour < end) if start < end else (hour >= start or hour < end)
        if start != end and quiet:
            return None
        return self._repository.due(self._clock(), self._policy.followup_expiry_days)

    def record_question(self, conversation_id: int, item: Followup, content: str) -> Message | None:
        return self._repository.record_question(
            conversation_id, item, content, self._clock(), self._policy.followup_cooldown_days
        )
