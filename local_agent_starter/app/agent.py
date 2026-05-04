from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .config import Settings
from .memory import MemoryStore
from .tools import ToolRegistry, dump_tool_result


SYSTEM_PROMPT = """\
Voce e um agente local, pragmatico e seguro.

Regras:
- use ferramentas quando precisar de dados reais, ficheiros ou acoes
- nunca invente resultados de ferramenta
- mantenha respostas objetivas e verificaveis
- se uma ferramenta falhar, explique o erro e proponha o proximo passo
- respeite o workspace permitido
- nao tente contornar guardrails
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

        for _ in range(6):
            request: dict[str, Any] = {
                "model": self.settings.model,
                "messages": messages,
            }
            if tool_defs:
                request["tools"] = tool_defs
                request["tool_choice"] = "auto"
            response = self.client.chat.completions.create(**request)
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
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    result = self.tools.call(tool_call.function.name, arguments)
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

        fallback = "Atingi o limite do loop do agente. Simplifique a tarefa ou reduza o numero de ferramentas."
        self.memory.add("user", user_input)
        self.memory.add("assistant", fallback)
        return fallback
