# Local Agent Starter

Projeto-base para um agente local mais completo, organizado para executar, ouvir, falar, ler, analisar, criar, gerar imagens, gerar sites, monitorar e obedecer comandos dentro de guardrails configurados.

## O que este projeto oferece

- loop de agente com tool calling
- memoria curta persistida em SQLite
- integracao com modelos locais via Ollama usando API compativel com OpenAI
- ferramentas controladas para ficheiros, HTTP e shell
- monitoramento do workspace por snapshot persistida
- voz de saida offline com `pyttsx3`
- captura de audio do microfone com `sounddevice` e `soundfile`
- transcricao e geracao de imagem via API multimodal opcional
- criacao automatica de sites HTML/CSS/JS
- exemplo minimo de MCP server em Python

## Estrutura

1. `app/main.py`
   - CLI interativa e comandos diretos
2. `app/agent.py`
   - loop do agente, modelo e tool calling
3. `app/tools.py`
   - registo de ferramentas e guardrails
4. `app/media.py`
   - voz, audio e imagem
5. `app/site_builder.py`
   - gerador de site base
6. `app/monitoring.py`
   - snapshot e diff do workspace
7. `app/memory.py`
   - memoria simples em SQLite
8. `mcp/simple_server.py`
   - exemplo de servidor MCP por `stdio`

## Requisitos

- Python 3.11+
- Ollama instalado e em execucao para o modelo textual
- um modelo local puxado no Ollama, por exemplo:
  - `ollama pull qwen3:8b`
- opcional: chave de API multimodal para imagem e transcricao

## Instalacao rapida

```powershell
cd C:\Users\User\Documents\GitHub\-\local_agent_starter
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Arranque rapido no Windows

Pode usar o script:

```powershell
.\run_agent.cmd
```

Na primeira execucao ele cria o ambiente virtual, instala dependencias em falta e abre o agente.

## Configuracao

Edite o `.env` para ajustar o modelo, permissoes e as funcionalidades multimodais.

Configuracao minima tipica:

```env
LOCAL_AGENT_MODEL=qwen3:8b
LOCAL_AGENT_BASE_URL=http://localhost:11434/v1
LOCAL_AGENT_API_KEY=ollama
LOCAL_AGENT_ALLOW_WRITE=true
LOCAL_AGENT_ENABLE_SHELL=true
```

Para voz e imagem com API multimodal:

```env
LOCAL_AGENT_MULTIMODAL_API_KEY=coloque_a_sua_chave
```

## Como correr

### Chat interativo

```powershell
.venv\Scripts\Activate.ps1
python -m app.main
```

### Diagnostico

```powershell
python -m app.main doctor
```

### Pergunta unica

```powershell
python -m app.main ask "analisa este projeto e cria um plano"
```

### Gravar e transcrever audio

```powershell
python -m app.main listen --seconds 6 --ask-agent
```

### Criar um site

```powershell
python -m app.main site --project portfolio --title "Meu Portfolio" --brief "Pagina de apresentacao com foco em servicos de IA"
```

### Gerar imagem

```powershell
python -m app.main image --prompt "um assistente de IA futurista numa mesa de trabalho"
```

## Comandos locais no chat

- `/help`
- `/doctor`
- `/monitor`
- `/monitor reset`
- `/listen 6`
- `/speak texto`
- `/site nome|titulo|brief`
- `/image ficheiro.png|prompt`

## Guardrails importantes

- todos os acessos a ficheiros ficam limitados ao workspace
- a shell usa uma allowlist configuravel
- operacoes multimodais dependem de configuracao explicita
- a escrita pode ser desligada por ambiente

## Testes de sanidade

```powershell
python -m unittest discover -s tests
```
