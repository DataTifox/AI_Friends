"""Atomically persist companion policy without discarding JSON documentation."""

from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile

from core.companion_policy import CompanionPolicy


class CompanionPolicyRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> CompanionPolicy:
        return CompanionPolicy.load(self.path)

    def comments(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        self.load()
        return json.loads(self.path.read_text(encoding="utf-8")).get("_comments") or {}

    def save(self, policy: CompanionPolicy) -> None:
        policy.validate()
        document = {}
        if self.path.exists():
            # Refuse to overwrite malformed configuration or unsupported fields.
            self.load()
            document = json.loads(self.path.read_text(encoding="utf-8"))
        document.update(asdict(policy))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
