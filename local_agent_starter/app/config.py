from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path(workspace: Path, raw_value: str | None, default: str) -> Path:
    candidate = Path(raw_value or default)
    if candidate.is_absolute():
        return candidate.resolve()
    return (workspace / candidate).resolve()


def _split_csv(raw_value: str | None, default: str) -> tuple[str, ...]:
    source = raw_value if raw_value is not None else default
    return tuple(part.strip() for part in source.split(",") if part.strip())


@dataclass(slots=True)
class Settings:
    model: str
    base_url: str
    api_key: str
    multimodal_base_url: str
    multimodal_api_key: str
    transcription_model: str
    image_model: str
    image_quality: str
    image_size: str
    memory_db: Path
    workspace: Path
    artifacts_dir: Path
    site_output_dir: Path
    image_output_dir: Path
    audio_output_dir: Path
    monitor_snapshot_file: Path
    max_memory_messages: int
    allow_write: bool
    enable_shell: bool
    shell_timeout_seconds: int
    http_timeout_seconds: int
    default_record_seconds: int
    tts_rate: int
    tts_voice_hint: str
    shell_allow_prefixes: tuple[str, ...]
    monitor_ignore_names: tuple[str, ...]

    @property
    def has_multimodal_api(self) -> bool:
        return bool(self.multimodal_api_key)


def load_settings() -> Settings:
    workspace = Path(os.getenv("LOCAL_AGENT_WORKSPACE", ".")).resolve()
    artifacts_dir = _resolve_path(workspace, os.getenv("LOCAL_AGENT_ARTIFACTS_DIR"), "./artifacts")
    return Settings(
        model=os.getenv("LOCAL_AGENT_MODEL", "qwen3:8b"),
        base_url=os.getenv("LOCAL_AGENT_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("LOCAL_AGENT_API_KEY", "ollama"),
        multimodal_base_url=os.getenv("LOCAL_AGENT_MULTIMODAL_BASE_URL", "https://api.openai.com/v1"),
        multimodal_api_key=os.getenv("LOCAL_AGENT_MULTIMODAL_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip(),
        transcription_model=os.getenv("LOCAL_AGENT_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe"),
        image_model=os.getenv("LOCAL_AGENT_IMAGE_MODEL", "gpt-image-1"),
        image_quality=os.getenv("LOCAL_AGENT_IMAGE_QUALITY", "medium"),
        image_size=os.getenv("LOCAL_AGENT_IMAGE_SIZE", "1024x1024"),
        memory_db=_resolve_path(workspace, os.getenv("LOCAL_AGENT_DB"), "./data/agent_memory.sqlite3"),
        workspace=workspace,
        artifacts_dir=artifacts_dir,
        site_output_dir=_resolve_path(
            workspace,
            os.getenv("LOCAL_AGENT_SITE_OUTPUT_DIR"),
            "./artifacts/sites",
        ),
        image_output_dir=_resolve_path(
            workspace,
            os.getenv("LOCAL_AGENT_IMAGE_OUTPUT_DIR"),
            "./artifacts/images",
        ),
        audio_output_dir=_resolve_path(
            workspace,
            os.getenv("LOCAL_AGENT_AUDIO_OUTPUT_DIR"),
            "./artifacts/audio",
        ),
        monitor_snapshot_file=_resolve_path(
            workspace,
            os.getenv("LOCAL_AGENT_MONITOR_SNAPSHOT"),
            "./data/workspace_snapshot.json",
        ),
        max_memory_messages=int(os.getenv("LOCAL_AGENT_MAX_MEMORY_MESSAGES", "14")),
        allow_write=_as_bool(os.getenv("LOCAL_AGENT_ALLOW_WRITE"), True),
        enable_shell=_as_bool(os.getenv("LOCAL_AGENT_ENABLE_SHELL"), True),
        shell_timeout_seconds=int(os.getenv("LOCAL_AGENT_SHELL_TIMEOUT_SECONDS", "30")),
        http_timeout_seconds=int(os.getenv("LOCAL_AGENT_HTTP_TIMEOUT_SECONDS", "20")),
        default_record_seconds=int(os.getenv("LOCAL_AGENT_DEFAULT_RECORD_SECONDS", "6")),
        tts_rate=int(os.getenv("LOCAL_AGENT_TTS_RATE", "185")),
        tts_voice_hint=os.getenv("LOCAL_AGENT_TTS_VOICE_HINT", "").strip(),
        shell_allow_prefixes=_split_csv(
            os.getenv("LOCAL_AGENT_SHELL_ALLOW_PREFIXES"),
            "Get-ChildItem,Get-Content,Get-Location,git status,git diff,git log,python --version,python -m http.server",
        ),
        monitor_ignore_names=_split_csv(
            os.getenv("LOCAL_AGENT_MONITOR_IGNORE_NAMES"),
            ".git,.venv,__pycache__,.pytest_cache",
        ),
    )
