"""OpenAI-compatible Chat Completions provider implemented with stdlib HTTP."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.llm_settings import LLMSettings
from services.llm.base import LLMConfigurationError, LLMProvider, LLMRequestError


class OpenAICompatibleProvider(LLMProvider):
    """Call the ``/chat/completions`` endpoint used by compatible providers."""

    def __init__(self, settings: LLMSettings, timeout_seconds: int = 60) -> None:
        try:
            settings.validate()
        except ValueError as error:
            raise LLMConfigurationError(str(error)) from error
        self._settings = settings
        self._timeout_seconds = timeout_seconds

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not messages:
            raise LLMRequestError("没有可发送给模型的上下文。")

        payload = json.dumps(
            {"model": self._settings.model.strip(), "messages": messages},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self._endpoint_url(),
            data=payload,
            headers={
                "Authorization": f"Bearer {self._settings.api_key.strip()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise LLMRequestError(self._http_error_message(error)) from error
        except URLError as error:
            raise LLMRequestError(f"无法连接模型服务：{error.reason}") from error
        except TimeoutError as error:
            raise LLMRequestError("模型请求超时，请稍后重试。") from error
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise LLMRequestError(f"模型响应无效：{error}") from error

        return self._extract_content(response_data)

    def _endpoint_url(self) -> str:
        base_url = self._settings.base_url.strip().rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    @staticmethod
    def _extract_content(response_data: Any) -> str:
        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMRequestError("模型响应中没有可用的助手回复。") from error
        if not isinstance(content, str) or not content.strip():
            raise LLMRequestError("模型返回了空回复。")
        return content.strip()

    @staticmethod
    def _http_error_message(error: HTTPError) -> str:
        detail = ""
        try:
            payload = json.loads(error.read().decode("utf-8"))
            detail = payload.get("error", {}).get("message", "")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            pass
        suffix = f"：{detail}" if detail else ""
        return f"模型服务请求失败（HTTP {error.code}）{suffix}"
