from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP


server = FastMCP("simple-local-server")
NOTES_DIR = Path(__file__).resolve().parent / "notes"


@server.tool()
def current_time() -> str:
    """Devolve a hora local atual em ISO-8601."""

    return datetime.now().astimezone().isoformat()


@server.tool()
def list_notes() -> list[str]:
    """Lista notas de exemplo expostas pelo MCP server."""

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(path.name for path in NOTES_DIR.glob("*.txt"))


@server.tool()
def read_note(name: str) -> str:
    """Le uma nota simples dentro da pasta notes."""

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    target = (NOTES_DIR / name).resolve()
    if target.parent != NOTES_DIR.resolve():
        raise ValueError("Caminho invalido.")
    if not target.exists():
        raise FileNotFoundError(f"Nota nao encontrada: {name}")
    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    server.run()
