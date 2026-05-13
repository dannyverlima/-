from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import httpx

from .config import Settings
from .media import generate_image, record_microphone, speak_text, transcribe_audio_file
from .monitoring import WorkspaceMonitor
from .site_builder import create_site_project, slugify


ToolFn = Callable[..., dict[str, Any]]
BLOCKED_SHELL_MARKERS = (";", "&&", "||", "|", ">", "<", "\n", "\r")
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".sqlite3",
    ".db",
    ".mp3",
    ".wav",
    ".pyc",
    ".exe",
    ".dll",
}


def _safe_path(workspace: Path, candidate: str) -> Path:
    raw_candidate = Path(candidate)
    target = raw_candidate.resolve() if raw_candidate.is_absolute() else (workspace / raw_candidate).resolve()
    if target != workspace and workspace not in target.parents:
        raise ValueError("Caminho fora do workspace permitido.")
    return target


def _relative_path(workspace: Path, target: Path) -> str:
    return str(target.relative_to(workspace)).replace("\\", "/")


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in chunk


@dataclass(slots=True)
class ToolRegistry:
    settings: Settings
    monitor: WorkspaceMonitor = field(init=False)

    def __post_init__(self) -> None:
        self.settings.memory_db.parent.mkdir(parents=True, exist_ok=True)
        self.settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.settings.site_output_dir.mkdir(parents=True, exist_ok=True)
        self.settings.image_output_dir.mkdir(parents=True, exist_ok=True)
        self.settings.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = WorkspaceMonitor(
            workspace=self.settings.workspace,
            snapshot_path=self.settings.monitor_snapshot_file,
            ignored_names=self.settings.monitor_ignore_names,
        )

    def definitions(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Devolve a data e hora atual em ISO-8601.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Lista ficheiros e pastas dentro do workspace permitido.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Subpasta relativa ao workspace."},
                            "recursive": {
                                "type": "boolean",
                                "description": "Se verdadeiro, lista tambem subpastas.",
                            },
                            "limit": {"type": "integer", "description": "Numero maximo de entradas."},
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Procura texto e nomes de ficheiros dentro do workspace permitido.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Texto a procurar."},
                            "path": {"type": "string", "description": "Subpasta relativa opcional."},
                            "max_matches": {"type": "integer", "description": "Limite maximo de resultados."},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Le um ficheiro de texto dentro do workspace permitido.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Caminho relativo ao workspace."}
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_workspace",
                    "description": "Resume a estrutura e os ficheiros mais recentes do workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Subpasta relativa opcional."},
                            "limit": {"type": "integer", "description": "Quantidade de ficheiros recentes."},
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "monitor_workspace",
                    "description": "Compara o estado atual do workspace com a ultima snapshot persistida.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reset": {
                                "type": "boolean",
                                "description": "Se verdadeiro, recria a baseline antes da comparacao.",
                            }
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "http_get",
                    "description": "Faz um GET HTTP simples para consultar uma API ou pagina.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL absoluta para consultar."}
                        },
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Gera uma imagem PNG a partir de um prompt quando a API multimodal estiver configurada.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Descricao da imagem."},
                            "output_path": {
                                "type": "string",
                                "description": "Caminho relativo do PNG. Se vazio, usa artifacts/images.",
                            },
                            "size": {"type": "string", "description": "Tamanho, por exemplo 1024x1024."},
                            "quality": {"type": "string", "description": "Qualidade low, medium ou high."},
                        },
                        "required": ["prompt"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "record_microphone",
                    "description": "Grava audio do microfone para um ficheiro WAV.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "seconds": {"type": "integer", "description": "Duracao da gravacao."},
                            "filename": {
                                "type": "string",
                                "description": "Nome do ficheiro WAV dentro de artifacts/audio.",
                            },
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "transcribe_audio_file",
                    "description": "Transcreve um ficheiro de audio usando a API multimodal configurada.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Caminho relativo do ficheiro de audio."}
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "speak_text",
                    "description": "Fala um texto usando a voz do sistema via pyttsx3.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Texto para leitura em voz alta."}
                        },
                        "required": ["text"],
                    },
                },
            },
        ]

        if self.settings.allow_write:
            tools.extend(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "description": "Escreve texto num ficheiro dentro do workspace permitido.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Caminho relativo ao workspace."},
                                    "content": {"type": "string", "description": "Conteudo a gravar."},
                                },
                                "required": ["path", "content"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "append_file",
                            "description": "Adiciona texto ao fim de um ficheiro dentro do workspace permitido.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Caminho relativo ao workspace."},
                                    "content": {"type": "string", "description": "Conteudo a acrescentar."},
                                },
                                "required": ["path", "content"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "create_directory",
                            "description": "Cria uma pasta dentro do workspace permitido.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Caminho relativo da pasta."}
                                },
                                "required": ["path"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "create_website_project",
                            "description": "Cria um site base com HTML, CSS e JavaScript.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Nome da pasta do site."},
                                    "title": {"type": "string", "description": "Titulo principal do site."},
                                    "brief": {"type": "string", "description": "Descricao resumida do site."},
                                    "overwrite": {"type": "boolean", "description": "Se verdadeiro, pode sobrescrever."},
                                },
                                "required": ["project_name", "title", "brief"],
                            },
                        },
                    },
                ]
            )

        if self.settings.enable_shell:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "run_shell_command",
                        "description": "Executa um comando PowerShell permitido por lista branca.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Comando PowerShell. Apenas prefixes da allowlist sao aceites.",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                }
            )

        return tools

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handlers: dict[str, ToolFn] = {
            "get_current_time": self.get_current_time,
            "list_files": self.list_files,
            "search_files": self.search_files,
            "read_file": self.read_file,
            "analyze_workspace": self.analyze_workspace,
            "monitor_workspace": self.monitor_workspace,
            "http_get": self.http_get,
            "generate_image": self.generate_image,
            "record_microphone": self.record_microphone,
            "transcribe_audio_file": self.transcribe_audio_file,
            "speak_text": self.speak_text,
        }
        if self.settings.allow_write:
            handlers["write_file"] = self.write_file
            handlers["append_file"] = self.append_file
            handlers["create_directory"] = self.create_directory
            handlers["create_website_project"] = self.create_website_project
        if self.settings.enable_shell:
            handlers["run_shell_command"] = self.run_shell_command
        if name not in handlers:
            raise ValueError(f"Ferramenta desconhecida: {name}")
        return handlers[name](**arguments)

    def diagnose(self) -> dict[str, Any]:
        checks: list[dict[str, Any]] = [
            {
                "name": "workspace",
                "ok": self.settings.workspace.exists(),
                "details": str(self.settings.workspace),
            },
            {
                "name": "memoria",
                "ok": self.settings.memory_db.parent.exists(),
                "details": str(self.settings.memory_db),
            },
            {
                "name": "escrita",
                "ok": self.settings.allow_write,
                "details": "LOCAL_AGENT_ALLOW_WRITE",
            },
            {
                "name": "shell",
                "ok": self.settings.enable_shell,
                "details": ", ".join(self.settings.shell_allow_prefixes),
            },
            {
                "name": "multimodal_api",
                "ok": self.settings.has_multimodal_api,
                "details": self.settings.multimodal_base_url,
            },
        ]

        dependency_checks = {
            "pyttsx3": self._module_available("pyttsx3"),
            "sounddevice": self._module_available("sounddevice"),
            "soundfile": self._module_available("soundfile"),
        }

        checks.extend(
            {
                "name": f"dependencia:{name}",
                "ok": ok,
                "details": "instalada" if ok else "em falta",
            }
            for name, ok in dependency_checks.items()
        )

        if "localhost:11434" in self.settings.base_url:
            checks.append(self._check_ollama())

        return {
            "ok": all(item["ok"] for item in checks if not item["name"].startswith("dependencia:")),
            "checks": checks,
        }

    def _check_ollama(self) -> dict[str, Any]:
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
            response.raise_for_status()
            models = [item.get("name", "") for item in response.json().get("models", [])]
            return {
                "name": "ollama",
                "ok": True,
                "details": ", ".join(models[:10]) or "sem modelos listados",
            }
        except Exception as exc:
            return {
                "name": "ollama",
                "ok": False,
                "details": str(exc),
            }

    @staticmethod
    def _module_available(module_name: str) -> bool:
        try:
            __import__(module_name)
        except ImportError:
            return False
        return True

    def get_current_time(self) -> dict[str, Any]:
        return {"now": datetime.now().astimezone().isoformat()}

    def list_files(self, path: str = "", recursive: bool = False, limit: int = 200) -> dict[str, Any]:
        folder = _safe_path(self.settings.workspace, path or ".")
        if not folder.exists() or not folder.is_dir():
            return {"ok": False, "error": "Pasta inexistente."}

        items: list[dict[str, Any]] = []
        iterator = folder.rglob("*") if recursive else folder.iterdir()
        for item in sorted(iterator, key=lambda p: (p.is_file(), str(p).lower())):
            relative = item.relative_to(self.settings.workspace)
            if any(part in self.settings.monitor_ignore_names for part in relative.parts):
                continue
            items.append(
                {
                    "name": item.name,
                    "type": "file" if item.is_file() else "directory",
                    "path": _relative_path(self.settings.workspace, item),
                }
            )
            if len(items) >= limit:
                break
        return {"ok": True, "items": items}

    def search_files(self, query: str, path: str = "", max_matches: int = 50) -> dict[str, Any]:
        folder = _safe_path(self.settings.workspace, path or ".")
        if not folder.exists() or not folder.is_dir():
            return {"ok": False, "error": "Pasta inexistente."}

        needle = query.lower()
        matches: list[dict[str, Any]] = []
        for file_path in sorted(folder.rglob("*")):
            if not file_path.is_file():
                continue
            relative = file_path.relative_to(self.settings.workspace)
            if any(part in self.settings.monitor_ignore_names for part in relative.parts):
                continue

            relative_text = _relative_path(self.settings.workspace, file_path)
            if needle in relative_text.lower():
                matches.append({"kind": "path", "path": relative_text})
                if len(matches) >= max_matches:
                    break

            if not _is_text_file(file_path):
                continue

            try:
                for line_number, line in enumerate(
                    file_path.read_text(encoding="utf-8", errors="replace").splitlines(),
                    start=1,
                ):
                    if needle in line.lower():
                        matches.append(
                            {
                                "kind": "content",
                                "path": relative_text,
                                "line": line_number,
                                "preview": line[:240],
                            }
                        )
                        if len(matches) >= max_matches:
                            break
            except OSError:
                continue

            if len(matches) >= max_matches:
                break

        return {"ok": True, "matches": matches, "query": query}

    def read_file(self, path: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        if not target.exists() or not target.is_file():
            return {"ok": False, "error": "Ficheiro inexistente."}
        if not _is_text_file(target):
            return {"ok": False, "error": "O ficheiro parece binario e nao sera lido como texto."}
        text = target.read_text(encoding="utf-8", errors="replace")
        return {"ok": True, "path": _relative_path(self.settings.workspace, target), "content": text[:20000]}

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"ok": True, "path": _relative_path(self.settings.workspace, target)}

    def append_file(self, path: str, content: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(content)
        return {"ok": True, "path": _relative_path(self.settings.workspace, target)}

    def create_directory(self, path: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        target.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "path": _relative_path(self.settings.workspace, target)}

    def analyze_workspace(self, path: str = "", limit: int = 20) -> dict[str, Any]:
        folder = _safe_path(self.settings.workspace, path or ".")
        if not folder.exists() or not folder.is_dir():
            return {"ok": False, "error": "Pasta inexistente."}

        extension_counts: dict[str, int] = {}
        files: list[Path] = []
        directories = 0

        for item in folder.rglob("*"):
            relative = item.relative_to(self.settings.workspace)
            if any(part in self.settings.monitor_ignore_names for part in relative.parts):
                continue
            if item.is_dir():
                directories += 1
                continue
            files.append(item)
            extension = item.suffix.lower() or "<sem_extensao>"
            extension_counts[extension] = extension_counts.get(extension, 0) + 1

        recent_files = sorted(files, key=lambda item: item.stat().st_mtime_ns, reverse=True)[:limit]
        return {
            "ok": True,
            "path": _relative_path(self.settings.workspace, folder),
            "summary": {
                "files": len(files),
                "directories": directories,
                "extensions": dict(sorted(extension_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:20]),
            },
            "recent_files": [
                {
                    "path": _relative_path(self.settings.workspace, item),
                    "size": item.stat().st_size,
                    "modified_at": datetime.fromtimestamp(item.stat().st_mtime).astimezone().isoformat(),
                }
                for item in recent_files
            ],
        }

    def monitor_workspace(self, reset: bool = False) -> dict[str, Any]:
        return self.monitor.scan(reset=reset)

    def http_get(self, url: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.settings.http_timeout_seconds, follow_redirects=True) as client:
            response = client.get(url)
        body = response.text[:6000]
        return {
            "ok": True,
            "status_code": response.status_code,
            "url": str(response.url),
            "body_preview": body,
        }

    def create_website_project(
        self,
        project_name: str,
        title: str,
        brief: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return create_site_project(
            workspace=self.settings.workspace,
            output_root=self.settings.site_output_dir,
            project_name=project_name,
            title=title,
            brief=brief,
            overwrite=overwrite,
        )

    def generate_image(
        self,
        prompt: str,
        output_path: str = "",
        size: str = "",
        quality: str = "",
    ) -> dict[str, Any]:
        filename = output_path.strip() or f"{slugify(prompt)[:40] or 'imagem'}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        relative_output = Path(filename)
        if not relative_output.suffix:
            relative_output = relative_output.with_suffix(".png")
        final_path = _safe_path(self.settings.workspace, str(relative_output if output_path else Path("artifacts/images") / relative_output.name))
        result = generate_image(
            settings=self.settings,
            prompt=prompt,
            output_path=final_path,
            size=size or self.settings.image_size,
            quality=quality or self.settings.image_quality,
        )
        result["path"] = _relative_path(self.settings.workspace, final_path)
        return result

    def record_microphone(self, seconds: int | None = None, filename: str = "") -> dict[str, Any]:
        duration = seconds or self.settings.default_record_seconds
        name = filename.strip() or f"mic-{datetime.now().strftime('%Y%m%d-%H%M%S')}.wav"
        target = _safe_path(self.settings.workspace, str(Path("artifacts/audio") / name))
        result = record_microphone(target, seconds=duration)
        result["path"] = _relative_path(self.settings.workspace, target)
        return result

    def transcribe_audio_file(self, path: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        if not target.exists() or not target.is_file():
            return {"ok": False, "error": "Ficheiro de audio inexistente."}
        result = transcribe_audio_file(self.settings, target)
        result["path"] = _relative_path(self.settings.workspace, target)
        return result

    def speak_text(self, text: str) -> dict[str, Any]:
        return speak_text(text=text, rate=self.settings.tts_rate, voice_hint=self.settings.tts_voice_hint)

    def run_shell_command(self, command: str) -> dict[str, Any]:
        stripped = command.strip()
        if not stripped:
            return {"ok": False, "error": "Comando vazio."}
        if any(marker in stripped for marker in BLOCKED_SHELL_MARKERS):
            return {"ok": False, "error": "Comando bloqueado por conter operadores nao permitidos."}
        if not any(stripped.startswith(prefix) for prefix in self.settings.shell_allow_prefixes):
            return {
                "ok": False,
                "error": "Comando bloqueado pela allowlist.",
                "allowed_prefixes": list(self.settings.shell_allow_prefixes),
            }
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", stripped],
            cwd=self.settings.workspace,
            capture_output=True,
            text=True,
            timeout=self.settings.shell_timeout_seconds,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout[:8000],
            "stderr": completed.stderr[:4000],
        }


def dump_tool_result(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
