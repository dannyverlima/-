# Local Agent Starter

Projeto-base para aprender a construir um agente local de forma segura e evolutiva.

## O que este projeto demonstra

- loop de agente com tool calling
- memoria curta persistida em SQLite
- integracao com modelos locais via Ollama usando API compativel com OpenAI
- ferramentas controladas de ficheiros, HTTP e sistema
- exemplo minimo de MCP server em Python

## Arquitetura recomendada

1. `app/main.py`
   - interface CLI
2. `app/agent.py`
   - loop do agente, chamadas ao modelo e execucao de ferramentas
3. `app/tools.py`
   - ferramentas com guardrails
4. `app/memory.py`
   - memoria simples em SQLite
5. `mcp/simple_server.py`
   - exemplo de servidor MCP por `stdio`

## Requisitos

- Python 3.11+
- Ollama instalado e em execucao
- um modelo local puxado no Ollama, por exemplo:
  - `ollama pull qwen3:8b`
  - ou outro modelo local compativel com tool calling

Nota:

- neste ambiente, o Ollama ainda nao estava instalado quando o projeto foi criado

## Instalacao

```powershell
cd C:\Users\User\.codex\worktrees\4dab\-\local_agent_starter
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Configuracao

Edite o `.env` se quiser mudar modelo, caminho da base de dados ou permissoes.

Configuracao minima tipica:

```env
LOCAL_AGENT_MODEL=qwen3:8b
LOCAL_AGENT_BASE_URL=http://localhost:11434/v1
LOCAL_AGENT_API_KEY=ollama
LOCAL_AGENT_ALLOW_WRITE=false
LOCAL_AGENT_ENABLE_SHELL=false
```

## Como correr

```powershell
cd C:\Users\User\.codex\worktrees\4dab\-\local_agent_starter
.venv\Scripts\Activate.ps1
python -m app.main
```

## Como pensar o crescimento do agente

### Etapa 1

- use so leitura de ficheiros e HTTP
- valide o comportamento com prompts pequenos
- mantenha um numero pequeno de ferramentas

### Etapa 2

- adicione RAG
- troque SQLite por PostgreSQL + pgvector se tiver varios utilizadores ou muitos documentos
- adicione tracing e logs ricos

### Etapa 3

- empacote integracoes reutilizaveis como MCP servers
- mova acoes sensiveis para ambientes isolados
- adicione aprovacoes humanas

## Porque esta stack e boa para aprender

- simples
- local-first
- barata
- auditavel
- facil de evoluir para algo mais serio
