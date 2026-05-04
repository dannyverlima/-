from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import httpx

from .config import Settings


ToolFn = Callable[..., dict[str, Any]]


def _safe_path(workspace: Path, candidate: str) -> Path:
    target = (workspace / candidate).resolve()
    if target != workspace and workspace not in target.parents:
        raise ValueError("Caminho fora do workspace permitido.")
    return target


@dataclass(slots=True)
class ToolRegistry:
    settings: Settings

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
                            "path": {
                                "type": "string",
                                "description": "Subpasta relativa ao workspace. Pode ficar vazia.",
                            }
                        },
                        "required": [],
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
                            "path": {
                                "type": "string",
                                "description": "Caminho relativo ao workspace.",
                            }
                        },
                        "required": ["path"],
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
        ]
        if self.settings.allow_write:
            tools.append(
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
                }
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
            "read_file": self.read_file,
            "http_get": self.http_get,
        }
        if self.settings.allow_write:
            handlers["write_file"] = self.write_file
        if self.settings.enable_shell:
            handlers["run_shell_command"] = self.run_shell_command
        if name not in handlers:
            raise ValueError(f"Ferramenta desconhecida: {name}")
        return handlers[name](**arguments)

    def get_current_time(self) -> dict[str, Any]:
        return {"now": datetime.now().astimezone().isoformat()}

    def list_files(self, path: str = "") -> dict[str, Any]:
        folder = _safe_path(self.settings.workspace, path or ".")
        if not folder.exists():
            return {"ok": False, "error": "Caminho inexistente."}
        items = []
        for item in sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            items.append(
                {
                    "name": item.name,
                    "type": "file" if item.is_file() else "directory",
                    "path": str(item.relative_to(self.settings.workspace)),
                }
            )
        return {"ok": True, "items": items[:200]}

    def read_file(self, path: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        if not target.exists() or not target.is_file():
            return {"ok": False, "error": "Ficheiro inexistente."}
        text = target.read_text(encoding="utf-8", errors="replace")
        return {"ok": True, "path": str(target.relative_to(self.settings.workspace)), "content": text[:20000]}

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        target = _safe_path(self.settings.workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(target.relative_to(self.settings.workspace))}

    def http_get(self, url: str) -> dict[str, Any]:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(url)
        body = response.text[:6000]
        return {
            "ok": True,
            "status_code": response.status_code,
            "url": str(response.url),
            "body_preview": body,
        }

    def run_shell_command(self, command: str) -> dict[str, Any]:
        if not any(command.startswith(prefix) for prefix in self.settings.shell_allow_prefixes):
            return {
                "ok": False,
                "error": "Comando bloqueado pela allowlist.",
                "allowed_prefixes": list(self.settings.shell_allow_prefixes),
            }
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            cwd=self.settings.workspace,
            capture_output=True,
            text=True,
            timeout=20,
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
