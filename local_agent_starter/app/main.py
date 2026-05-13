from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .agent import LocalAgent
from .config import Settings, load_settings
from .memory import MemoryStore
from .tools import ToolRegistry


def _load_environment() -> None:
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)


def _build_runtime() -> tuple[Settings, ToolRegistry, LocalAgent]:
    _load_environment()
    settings = load_settings()
    memory = MemoryStore(settings.memory_db)
    tools = ToolRegistry(settings)
    agent = LocalAgent(settings=settings, memory=memory, tools=tools)
    return settings, tools, agent


def _print_payload(payload: Any) -> None:
    if isinstance(payload, str):
        print(payload)
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agente local multimodal com ferramentas e guardrails.")
    subparsers = parser.add_subparsers(dest="command")

    ask_parser = subparsers.add_parser("ask", help="Envia uma pergunta unica ao agente.")
    ask_parser.add_argument("prompt", nargs="+")

    subparsers.add_parser("doctor", help="Mostra diagnostico rapido do ambiente.")

    listen_parser = subparsers.add_parser("listen", help="Grava audio e transcreve.")
    listen_parser.add_argument("--seconds", type=int, default=None)
    listen_parser.add_argument(
        "--ask-agent",
        action="store_true",
        help="Depois da transcricao, envia o texto para o agente responder.",
    )

    monitor_parser = subparsers.add_parser("monitor", help="Compara o workspace com a ultima snapshot.")
    monitor_parser.add_argument("--reset", action="store_true")

    speak_parser = subparsers.add_parser("speak", help="Ler texto em voz alta.")
    speak_parser.add_argument("text", nargs="+")

    site_parser = subparsers.add_parser("site", help="Cria um site base no workspace.")
    site_parser.add_argument("--project", required=True)
    site_parser.add_argument("--title", required=True)
    site_parser.add_argument("--brief", required=True)
    site_parser.add_argument("--overwrite", action="store_true")

    image_parser = subparsers.add_parser("image", help="Gera uma imagem PNG.")
    image_parser.add_argument("--prompt", required=True)
    image_parser.add_argument("--output", default="")
    image_parser.add_argument("--size", default="")
    image_parser.add_argument("--quality", default="")

    return parser


def _interactive_help() -> None:
    print(
        "\nComandos locais:\n"
        "  /help                       mostra esta ajuda\n"
        "  /doctor                     diagnostico rapido\n"
        "  /monitor                    mostra alteracoes do workspace\n"
        "  /monitor reset              recria a baseline de monitoramento\n"
        "  /listen [segundos]          grava audio e transcreve\n"
        "  /speak <texto>              fala o texto no sistema\n"
        "  /site nome|titulo|brief     cria um site base\n"
        "  /image ficheiro|prompt      gera imagem PNG\n"
        "  /quit                       termina a sessao\n"
    )


def _handle_interactive_command(raw_input: str, tools: ToolRegistry, agent: LocalAgent) -> bool:
    command, _, rest = raw_input[1:].partition(" ")
    command = command.lower().strip()
    rest = rest.strip()

    if command in {"quit", "exit"}:
        print("Ate ja.")
        return False
    if command == "help":
        _interactive_help()
        return True
    if command == "doctor":
        _print_payload(tools.diagnose())
        return True
    if command == "monitor":
        _print_payload(tools.monitor_workspace(reset=rest.lower() == "reset"))
        return True
    if command == "listen":
        seconds = int(rest) if rest else tools.settings.default_record_seconds
        recorded = tools.record_microphone(seconds=seconds)
        transcript = tools.transcribe_audio_file(recorded["path"])
        _print_payload(transcript)
        if transcript.get("ok") and transcript.get("text"):
            print("\nAgente> " + agent.ask(transcript["text"]))
        return True
    if command == "speak":
        _print_payload(tools.speak_text(rest))
        return True
    if command == "site":
        parts = [part.strip() for part in rest.split("|")]
        if len(parts) != 3:
            print("Uso: /site nome|titulo|brief")
            return True
        _print_payload(
            tools.create_website_project(
                project_name=parts[0],
                title=parts[1],
                brief=parts[2],
            )
        )
        return True
    if command == "image":
        parts = [part.strip() for part in rest.split("|", maxsplit=1)]
        if len(parts) != 2:
            print("Uso: /image ficheiro.png|prompt da imagem")
            return True
        _print_payload(tools.generate_image(prompt=parts[1], output_path=parts[0]))
        return True

    print("Comando local desconhecido. Use /help.")
    return True


def _run_chat(settings: Settings, tools: ToolRegistry, agent: LocalAgent) -> int:
    print("Agente local pronto.")
    print(f"Modelo textual: {settings.model}")
    print(f"Workspace: {settings.workspace}")
    print("Use /help para comandos locais e 'sair' para terminar.")

    while True:
        try:
            user_input = input("\nVoce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSessao terminada.")
            return 0

        if not user_input:
            continue
        if user_input.startswith("/"):
            should_continue = _handle_interactive_command(user_input, tools, agent)
            if not should_continue:
                return 0
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            print("Ate ja.")
            return 0

        try:
            answer = agent.ask(user_input)
        except Exception as exc:  # pragma: no cover - CLI guardrail
            print(f"Erro: {exc}")
            continue
        print(f"\nAgente> {answer}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    settings, tools, agent = _build_runtime()

    if args.command == "ask":
        print(agent.ask(" ".join(args.prompt)))
        return 0
    if args.command == "doctor":
        _print_payload(tools.diagnose())
        return 0
    if args.command == "listen":
        recorded = tools.record_microphone(seconds=args.seconds or settings.default_record_seconds)
        transcript = tools.transcribe_audio_file(recorded["path"])
        _print_payload(transcript)
        if args.ask_agent and transcript.get("ok") and transcript.get("text"):
            print("\nAgente> " + agent.ask(transcript["text"]))
        return 0
    if args.command == "monitor":
        _print_payload(tools.monitor_workspace(reset=args.reset))
        return 0
    if args.command == "speak":
        _print_payload(tools.speak_text(" ".join(args.text)))
        return 0
    if args.command == "site":
        _print_payload(
            tools.create_website_project(
                project_name=args.project,
                title=args.title,
                brief=args.brief,
                overwrite=args.overwrite,
            )
        )
        return 0
    if args.command == "image":
        _print_payload(
            tools.generate_image(
                prompt=args.prompt,
                output_path=args.output,
                size=args.size,
                quality=args.quality,
            )
        )
        return 0

    return _run_chat(settings, tools, agent)


if __name__ == "__main__":
    raise SystemExit(main())
