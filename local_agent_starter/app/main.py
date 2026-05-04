from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from .agent import LocalAgent
from .config import load_settings
from .memory import MemoryStore
from .tools import ToolRegistry


def main() -> None:
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)

    settings = load_settings()
    memory = MemoryStore(settings.memory_db)
    tools = ToolRegistry(settings)
    agent = LocalAgent(settings=settings, memory=memory, tools=tools)

    print("Agente local pronto.")
    print(f"Modelo: {settings.model}")
    print(f"Workspace: {settings.workspace}")
    print("Escreva 'sair' para terminar.")

    while True:
        try:
            user_input = input("\nVoce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSessao terminada.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            print("Ate ja.")
            break

        try:
            answer = agent.ask(user_input)
        except Exception as exc:  # pragma: no cover - CLI guardrail
            print(f"Erro: {exc}")
            continue
        print(f"\nAgente> {answer}")


if __name__ == "__main__":
    main()
