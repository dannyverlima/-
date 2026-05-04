from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    model: str
    base_url: str
    api_key: str
    memory_db: Path
    workspace: Path
    max_memory_messages: int
    allow_write: bool
    enable_shell: bool
    shell_allow_prefixes: tuple[str, ...]


def load_settings() -> Settings:
    workspace = Path(os.getenv("LOCAL_AGENT_WORKSPACE", ".")).resolve()
    return Settings(
        model=os.getenv("LOCAL_AGENT_MODEL", "qwen3:8b"),
        base_url=os.getenv("LOCAL_AGENT_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("LOCAL_AGENT_API_KEY", "ollama"),
        memory_db=Path(os.getenv("LOCAL_AGENT_DB", "./data/agent_memory.sqlite3")).resolve(),
        workspace=workspace,
        max_memory_messages=int(os.getenv("LOCAL_AGENT_MAX_MEMORY_MESSAGES", "14")),
        allow_write=_as_bool(os.getenv("LOCAL_AGENT_ALLOW_WRITE"), False),
        enable_shell=_as_bool(os.getenv("LOCAL_AGENT_ENABLE_SHELL"), False),
        shell_allow_prefixes=tuple(
            part.strip()
            for part in os.getenv(
                "LOCAL_AGENT_SHELL_ALLOW_PREFIXES",
                "Get-ChildItem,Get-Content,git status,git diff,git log,python --version",
            ).split(",")
            if part.strip()
        ),
    )
