from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .config import Settings
from .memory import MemoryStore
from .tools import ToolRegistry, dump_tool_result


SYSTEM_PROMPT = """\
Voce e um agente local operativo, pragmatico e seguro.

Capacidades esperadas:
- ouvir e transcrever audio quando as dependencias estiverem configuradas
- falar com saida de voz
- ler e analisar ficheiros
- criar conteudo, sites e artefactos no workspace
- gerar imagens quando houver API multimodal configurada
- monitorar alteracoes no workspace
- executar comandos permitidos e obedecer ao utilizador dentro das permissoes ativas

Regras:
- use ferramentas sempre que precisar de dados reais, ficheiros ou acoes
- nunca invente o resultado de uma ferramenta
- mantenha respostas objetivas, claras e verificaveis
- se uma ferramenta falhar, explique o erro e proponha um proximo passo pratico
- respeite o workspace permitido e as guardrails das ferramentas
- para criar sites, prefira a ferramenta especializada antes de escrever ficheiros manualmente
- para audio e imagem, diga claramente quando a funcionalidade depende de configuracao externa
"""


class LocalAgent:
    def __init__(self, settings: Settings, memory: MemoryStore, tools: ToolRegistry) -> None:
        self.settings = settings
        self.memory = memory
        self.tools = tools
        self.client = OpenAI(base_url=settings.base_url, api_key=settings.api_key)

    def ask(self, user_input: str) -> str:
        history = self.memory.load_recent(self.settings.max_memory_messages)
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        tool_defs = self.tools.definitions()

        for _ in range(8):
            request: dict[str, Any] = {
                "model": self.settings.model,
                "messages": messages,
            }
            if tool_defs:
                request["tools"] = tool_defs
                request["tool_choice"] = "auto"

            try:
                response = self.client.chat.completions.create(**request)
            except Exception as exc:  # pragma: no cover - remote dependency
                raise RuntimeError(
                    "Falha ao contactar o modelo configurado. "
                    "Confirme LOCAL_AGENT_BASE_URL, LOCAL_AGENT_MODEL e se o backend esta ativo."
                ) from exc

            message = response.choices[0].message

            if message.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                            for tool_call in message.tool_calls
                        ],
                    }
                )

                for tool_call in message.tool_calls:
                    try:
                        arguments = json.loads(tool_call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}

                    try:
                        result = self.tools.call(tool_call.function.name, arguments)
                    except Exception as exc:  # pragma: no cover - defensive wrapper
                        result = {
                            "ok": False,
                            "tool": tool_call.function.name,
                            "error": str(exc),
                        }

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": dump_tool_result(result),
                        }
                    )
                continue

            final_text = (message.content or "").strip()
            if not final_text:
                final_text = "Nao consegui produzir uma resposta util."
            self.memory.add("user", user_input)
            self.memory.add("assistant", final_text)
            return final_text

        fallback = "Atingi o limite do loop do agente. Tente simplificar a tarefa em passos menores."
        self.memory.add("user", user_input)
        self.memory.add("assistant", fallback)
        return fallback
