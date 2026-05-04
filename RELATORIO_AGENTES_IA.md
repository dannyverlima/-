


# Relatorio: Como Funcionam os Agentes de IA e Como Criar o Seu

Data de referencia: 1 de maio de 2026

## Escopo

Voce pediu uma analise de "todos os agentes IA famosos". Como isso muda muito rapido, eu usei um criterio pratico:

- incluir as familias e plataformas mais influentes, com documentacao tecnica publica ou oficial
- focar no que realmente interessa para engenharia: LLM, MCP, memoria, ferramentas, execucao, multimodalidade e integracoes
- separar o que e fato documentado do que e inferencia tecnica

Nao inclui sistemas muito fechados, com pouca documentacao primaria publica sobre arquitetura interna, como se fossem equivalentes a frameworks abertos. Quando a capacidade e publica, eu menciono. Quando a arquitetura exata nao e publica, eu marco isso como inferencia.

## Resumo Executivo

Quase todos os agentes de IA famosos seguem a mesma estrutura-base:

1. um modelo central de linguagem ou multimodal
2. um loop de execucao que recebe objetivo, pensa, chama ferramentas e valida o resultado
3. um sistema de estado ou memoria
4. uma camada de ferramentas, APIs, MCPs ou integracoes
5. guardrails: permissao, revisao humana, logs, tracing e limites

O que muda entre eles nao e o conceito central. O que muda e:

- como eles orquestram passos e subagentes
- como expoem ferramentas
- como persistem estado
- o nivel de autonomia
- o nivel de seguranca e observabilidade

## O que os agentes mais famosos fazem melhor

### OpenAI Agents SDK

Como funciona:

- trata agentes como aplicacoes que planeiam, chamam ferramentas, colaboram entre especialistas e mantem estado suficiente para completar trabalho multi-etapa
- suporta orquestracao, handoffs, guardrails, state/results e sandbox agents
- tambem tem computer use, em que o modelo pede screenshots e devolve acoes de interface

Objetivo:

- criar agentes de producao, especialmente quando o agente precisa de ferramentas, ciclo de execucao e integracao com ambientes de trabalho

Ponto forte:

- muito forte em loop de execucao, ferramentas, sandbox e observabilidade

Limite:

- para uso local puro, ainda exige mais trabalho de infraestrutura do que uma stack totalmente offline

### Claude + MCP + Computer Use

Como funciona:

- o Claude usa ferramentas e pode operar computador com um loop agente-ferramenta
- o MCP padroniza como ligar o agente a ferramentas, recursos, prompts e servidores remotos ou locais
- o protocolo usa arquitetura host -> client -> server e trabalha com tools, resources e prompts

Objetivo:

- ser um ecossistema padrao para ligar agentes a software, dados, ficheiros e sistemas empresariais

Ponto forte:

- excelente separacao entre "modelo" e "camada de integracao"

Limite:

- MCP resolve conectividade e contexto, nao resolve sozinho planeamento, memoria, avaliacao ou seguranca operacional

### Google ADK

Como funciona:

- o ADK trata o agente como uma unidade autonoma de execucao
- tem LLM Agents, mas tambem Workflow Agents para sequencia, paralelo e loop sem depender de um LLM para controlar todo o fluxo
- suporta Python, TypeScript, Go e Java

Objetivo:

- aproximar desenvolvimento de agentes de engenharia de software tradicional

Ponto forte:

- muito bom quando voce quer misturar autonomia com passos deterministicos

Limite:

- ecossistema menos simples para MVPs muito pequenos do que uma stack Python enxuta

### Microsoft AutoGen

Como funciona:

- framework para construir aplicacoes conversacionais single-agent e multi-agent
- a unidade central e o agente que envia, recebe e responde mensagens, podendo usar modelos, ferramentas e input humano

Objetivo:

- multiagente baseado em troca de mensagens e especializacao de papeis

Ponto forte:

- bom para simulacao de equipas de agentes e pipelines colaborativos

Limite:

- e facil criar complexidade demais cedo demais

### LangGraph

Como funciona:

- framework para construir agentes de linguagem resilientes como grafos
- excelente para fluxos stateful, de longa duracao, com branching, ciclos, interrupcoes e persistencia

Objetivo:

- agentes confiaveis em producao, especialmente quando o comportamento precisa ser controlado

Ponto forte:

- uma das melhores opcoes para workflows de agentes com estado e recuperacao

Limite:

- mais baixo nivel; excelente em producao, menos amigavel para iniciantes do que um loop simples

### CrewAI

Como funciona:

- agentes com papel, objetivo, memoria, ferramentas, delegacao e colaboracao
- distingue bem capacidades de acao e capacidades de contexto
- ferramentas, MCPs e apps servem para agir
- skills e knowledge servem para moldar como o agente pensa

Objetivo:

- montar crews ou equipas de agentes com papeis bem definidos

Ponto forte:

- modelo mental facil para negocio e automacao

Limite:

- se mal desenhado, vira excesso de agentes para problemas simples

### Hugging Face smolagents

Como funciona:

- agente muito leve, normalmente centrado em codigo, ferramentas e execucao simples
- otimo para prototipos curtos e estudo

Objetivo:

- aprender rapido, validar ideia rapido

Ponto forte:

- simples e leve

Limite:

- nao e a primeira escolha para sistemas mais robustos e governados

### AutoGPT Platform

Como funciona:

- plataforma com frontend, server, marketplace, blocos e workflows
- foca em agentes continuos e automacoes

Objetivo:

- automatizar processos de negocio e workflows long-running

Ponto forte:

- boa orientacao a blocos e automacao

Limite:

- menos didatico para quem quer compreender o nucleo tecnico do agente desde a base

### Devin

Como funciona:

- agente de software com arquitetura separando "brain" e "devbox"
- o brain fica na cloud; o devbox e o ambiente seguro onde o agente corre codigo, shell, editor e browser

Objetivo:

- engenharia de software autonoma ou semi-autonoma

Ponto forte:

- muito forte para tarefas de codigo, backlog, refatoracao, CI e modernizacao

Limite:

- nao e uma stack local-first; e uma arquitetura de produto fechada

### Ollama como stack local

Como funciona:

- nao e um framework de agente completo, mas um runtime local importantissimo
- expoe modelos locais, tool calling e compatibilidade com partes da API OpenAI, inclusive `/v1/responses`

Objetivo:

- rodar modelos localmente, com privacidade, baixo custo marginal e integracao simples

Ponto forte:

- ideal para o primeiro agente local

Limite:

- a inteligencia do agente ainda depende do modelo e do loop que voce construir por cima

## Como estes sistemas funcionam tecnicamente

### 1. LLM

O LLM e o cerebro linguistico do agente.

Funcoes principais:

- interpretar instrucoes
- decompor objetivos
- escolher ferramentas
- resumir resultados
- decidir proximo passo

Na pratica, o LLM nao "faz" a acao sozinho. Ele:

1. recebe contexto
2. gera uma resposta textual ou uma chamada estruturada de ferramenta
3. recebe o resultado da ferramenta
4. continua o raciocinio com base nesse resultado

Por isso, um agente nao e apenas um LLM. Um agente e um LLM dentro de um loop operacional.

### 2. MCP

O MCP e uma camada padrao para conectar agentes a sistemas externos.

Ele nao substitui o LLM.
Ele nao substitui a base de dados.
Ele nao substitui a logica do seu produto.

Ele serve para padronizar:

- descoberta de ferramentas
- leitura de recursos
- prompts reutilizaveis
- transporte local por stdio
- transporte remoto por HTTP streaming

O MCP tem tres primitivas principais no lado do servidor:

- tools: funcoes executaveis
- resources: dados contextuais
- prompts: templates reutilizaveis

Conclusao pratica:

- LLM decide
- MCP expoe capacidades
- seu runtime executa
- seus guardrails autorizam ou bloqueiam

### 3. Redes Neuronais

Redes neuronais sao a base matematica que torna tudo isto possivel.

No nivel mais simples:

- entram dados
- camadas aplicam pesos e transformacoes
- o modelo aprende padroes ao ajustar esses pesos

Nos agentes modernos, as familias mais importantes sao:

- Transformers para linguagem, visao e multimodalidade
- modelos de difusao ou geracao visual para imagem
- redes de visao para deteccao, segmentacao, pose e tracking

O agente em si normalmente mistura varias redes:

- um LLM para linguagem e planeamento
- um modelo de fala para transcricao
- um modelo de visao para perceber imagens ou video
- por vezes um modelo extra para embeddings e recuperacao

## Como sao feitas as capacidades que voce pediu

### Geracao de imagem

Fato documentado:

- a OpenAI documenta que os seus modelos GPT Image geram e editam imagens

Inferencia tecnica:

- a arquitetura exata de modelos fechados como GPT Image nao e totalmente publica
- o padrao atual do mercado combina codificacao textual, representacoes latentes e um gerador visual capaz de seguir instrucoes detalhadas

Em termos praticos:

1. o prompt vira representacao numerica
2. o modelo gera uma representacao visual coerente com o texto
3. um decoder transforma isso em imagem final
4. etapas internas refinam detalhe, texto na imagem, composicao e coerencia

### Reconhecimento de voz

Exemplo forte: Whisper.

Fato documentado:

- o Whisper e um ASR treinado em 680.000 horas de dados
- a arquitetura usa um encoder-decoder Transformer
- o audio e convertido em log-Mel spectrogram e depois transformado em texto

Em termos praticos:

1. captura de audio
2. normalizacao e recorte em janelas
3. transformacao para espectrograma
4. encoder extrai padroes temporais
5. decoder produz texto, idioma, timestamps e, em alguns casos, traducao

### Reconhecimento de movimento

Normalmente nao e "um unico modelo".
E um pipeline:

1. pose estimation ou tracking
2. extracao de landmarks ou trajectorias
3. classificador de gesto, postura ou acao

Exemplos atuais:

- ML Kit Pose Detection detecta 33 landmarks do corpo
- Ultralytics YOLO faz pose e tracking em tempo real

Em termos praticos:

- para fitness, ergonomia e gestos simples, MediaPipe/ML Kit Pose costuma ser suficiente
- para vigilancia, robotica ou video mais pesado, YOLO + tracking + classificador temporal e melhor

### Reconhecimento de imagem

Aqui entram varias subtarefas:

- classificacao: "que objeto e este?"
- deteccao: "onde esta o objeto?"
- segmentacao: "que pixels pertencem ao objeto?"
- OCR: "que texto ha na imagem?"
- VLM: "o que esta a acontecer nesta imagem?"

Exemplos fortes:

- YOLO para detect, classify, segment, pose e track
- SAM 3 para segmentacao por conceito
- modelos multimodais para interpretar imagem e texto ao mesmo tempo

### Obedecer comandos

Um agente nao "obedece" por magia.
Ele obedece porque o sistema mistura:

- system prompt
- schema de ferramentas
- regras de permissao
- loop de planeamento
- validacao de outputs

Na pratica:

1. o utilizador pede uma tarefa
2. o LLM decide se responde diretamente ou chama uma ferramenta
3. a aplicacao executa a ferramenta
4. o resultado volta ao modelo
5. o modelo fecha a resposta ou continua o trabalho

### Interacao com computador e aplicacoes

Os sistemas mais modernos fazem isto via "computer use".

Fluxo normal:

1. o modelo recebe um objetivo
2. pede screenshot ou estado visual
3. identifica campos, botoes, menus e elementos
4. devolve acoes como clicar, escrever, fazer scroll ou esperar
5. o ambiente executa
6. o modelo observa o novo estado

Isto exige:

- ambiente sandbox
- lista de acoes permitidas
- validacao humana para tarefas destrutivas

### Conexao a APIs

Ha tres formas comuns:

- tools nativas da aplicacao
- MCP servers
- SDKs diretos no codigo

Padrao ideal:

1. descrever a API como ferramenta com schema claro
2. o LLM escolhe a ferramenta
3. o runtime executa HTTP
4. a resposta e devolvida ao modelo em formato limpo

### Conectividade com base de dados

Padrao ideal:

- o agente nunca fala SQL livre contra producao sem limites
- ele fala com uma ferramenta controlada
- essa ferramenta valida, audita e limita o acesso

Tipos de integracao mais comuns:

- SQL transacional: PostgreSQL, SQLite
- busca textual: SQLite FTS5 ou Postgres full-text
- busca vetorial: pgvector ou Qdrant

## Melhor plano para criar o seu proprio agente local

### Fase 1: MVP local inteligente

Objetivo:

- agente conversacional com ferramentas, memoria curta e execucao local

Stack recomendada:

- linguagem: Python
- runtime do modelo: Ollama
- LLM local: Qwen3 8B ou 14B para texto e tool calling; Gemma 4 E4B se voce quiser footprint menor; Gemma 4 26B/31B se tiver hardware forte
- memoria: SQLite
- busca textual: SQLite FTS5
- integracoes: ferramentas Python primeiro
- MCP: adicionar depois que o nucleo estiver estavel

### Fase 2: agente com visao, voz e RAG

Adicionar:

- Whisper para speech-to-text
- YOLO ou ML Kit/MediaPipe para pose e tracking
- embeddings e busca vetorial
- pgvector ou Qdrant, consoante a carga

### Fase 3: agente operacional serio

Adicionar:

- permissao humana para acoes destrutivas
- tracing e logs
- retries, timeouts e limites
- politicas de acesso por ferramenta
- isolamento de shell e browser

## Qual linguagem e mais eficiente

### Melhor escolha geral: Python

Por que:

- melhor ecossistema para IA aplicada
- melhores SDKs para modelos, visao, audio e RAG
- integracao facil com OpenAI-compatible APIs, Ollama, MCP, SQLite, Postgres, HTTP e automacao
- fastest path para aprender e entregar

Python e a linguagem mais eficiente para construir o primeiro agente realmente util.

### Segunda melhor: TypeScript

Melhor se:

- voce quer integrar forte com web, Electron, extensoes ou frontends
- quer usar ADK TS, browser automations e Node ecosystem

### Terceira camada: Rust

Use Rust para:

- MCP servers criticos
- componentes que exigem performance ou seguranca extrema
- motores de processamento pesado

Nao recomendo Rust como primeira linguagem do agente inteiro, a nao ser que privacidade, performance e hardening sejam o centro do projeto.

## Melhor base de dados

### Para comecar: SQLite + FTS5

Use quando:

- projeto local
- um utilizador ou poucos utilizadores
- baixo custo operacional
- memoria e logs do agente

Vantagens:

- zero infraestrutura
- muito confiavel
- FTS5 para busca textual nativa

### Melhor padrao para producao geral: PostgreSQL + pgvector

Esta e a minha recomendacao principal.

Por que:

- dados relacionais e vetoriais no mesmo sitio
- JOINs, ACID, auditoria, backup e ecossistema maduro
- pgvector suporta busca exata e aproximada

Quando escolher:

- quando o agente precisa de utilizadores, sessoes, documentos, permissoes, logs e RAG no mesmo sistema

### Quando usar Qdrant

Use Qdrant se:

- a busca vetorial e o centro do produto
- o volume de embeddings e alto
- quer separar retrieval do banco transacional

Resumo pratico:

- MVP local: SQLite
- produto serio geral: PostgreSQL + pgvector
- retrieval massivo especializado: Qdrant

## Que LLMs usar

### Para agente local de texto e ferramentas

Melhores apostas atuais:

- Qwen3 8B ou 14B: excelente relacao entre tamanho, raciocinio e uso com ferramentas
- Qwen3 32B: muito forte se voce tiver hardware suficiente
- Gemma 4 E4B: boa opcao edge/local leve
- Gemma 4 26B ou 31B: melhor para maior qualidade offline e workflows agentic

### Para multimodal local

- Phi-4-multimodal: texto, audio e visao na mesma familia
- Gemma 4 E2B/E4B: interessante para edge, imagem e audio em hardware menor

### Para transcricao de voz

- Whisper continua sendo uma escolha muito forte e pratica

### Para visao operacional

- YOLO para deteccao, tracking e pose
- SAM 3 para segmentacao por conceito
- modelos multimodais quando precisa interpretar a cena em linguagem natural

## Que MCP usar

Recomendacao:

- use o SDK oficial `mcp` em Python
- comece com servidores locais pequenos por stdio
- use HTTP/OAuth apenas quando realmente precisar de servidores remotos multiutilizador

Padrao ideal:

1. ferramentas Python nativas no MVP
2. depois empacotar integracoes reutilizaveis como MCP servers
3. so depois abrir para HTTP e auth

## Que redes neuronais usar por capacidade

### Linguagem e planeamento

- Transformers LLM

### Voz

- encoder-decoder Transformer de ASR, como Whisper

### Imagem

- modelos de visao e visao-linguagem
- geradores visuais modernos para image generation

### Movimento

- pose estimation + tracking + classificador temporal

### Embeddings e RAG

- modelo de embeddings dedicado
- indice vetorial ou hybrid search

## Arquitetura que eu recomendo para voce

### Arquitetura-base

1. Interface CLI local
2. Agente Python
3. LLM local via Ollama
4. Ferramentas controladas em Python
5. SQLite para memoria, logs e configuracoes
6. PostgreSQL + pgvector quando o projeto crescer
7. MCP para integrar sistemas externos e reutilizar ferramentas
8. YOLO/MediaPipe/Whisper conforme as capacidades multimodais forem entrando

### Porque esta arquitetura e a melhor para aprender e crescer

- comeca simples
- funciona offline
- tem baixo custo
- e auditavel
- permite subir de nivel sem reescrever tudo

## Como aplicar na pratica

### Se o seu objetivo e um assistente pessoal local

Use:

- Python
- Ollama
- Qwen3 8B ou Gemma 4 E4B
- SQLite
- ferramentas de ficheiro, web e calendario

### Se o seu objetivo e um agente que controla o computador

Use:

- ambiente sandbox
- computer use apenas com lista branca
- confirmacao humana para acoes sensiveis

### Se o seu objetivo e analise de imagem e movimento

Use:

- YOLO para deteccao e tracking
- pose estimation para landmarks
- um classificador simples para gestos ou rotinas

### Se o seu objetivo e agente de negocio com documentos

Use:

- PostgreSQL + pgvector
- embeddings
- RAG
- MCP servers para CRM, email, ERP e BI

## O que eu criei neste workspace para voce

Eu tambem criei um projeto-base local em Python com:

- agente local com loop de ferramentas
- memoria em SQLite
- integracao OpenAI-compatible para Ollama
- exemplo simples de MCP server
- script `.cmd` para abrir este relatorio em verde

Veja a pasta `local_agent_starter`.

## Fontes Principais

Fontes oficiais e atuais usadas nesta analise:

- OpenAI Agents SDK: https://developers.openai.com/api/docs/guides/agents
- OpenAI computer use: https://developers.openai.com/api/docs/guides/tools-computer-use
- OpenAI images and vision: https://developers.openai.com/api/docs/guides/images-vision
- OpenAI Whisper: https://openai.com/index/whisper/
- MCP introducao: https://modelcontextprotocol.io/docs/getting-started/intro
- MCP arquitetura: https://modelcontextprotocol.io/docs/learn/architecture
- MCP SDKs: https://modelcontextprotocol.io/docs/sdk
- MCP Python SDK instalacao: https://modelcontextprotocol.github.io/python-sdk/installation/
- MCP seguranca: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- MCP autorizacao: https://modelcontextprotocol.io/docs/tutorials/security/authorization
- Anthropic computer use: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
- Google ADK overview: https://adk.dev/agents/
- AutoGen: https://microsoft.github.io/autogen/stable/index.html
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- CrewAI agents: https://docs.crewai.com/en/concepts/agents
- CrewAI capabilities: https://docs.crewai.com/en/concepts/agent-capabilities
- smolagents: https://huggingface.co/docs/smolagents/index
- AutoGPT docs: https://docs.agpt.co/
- Devin intro: https://docs.devin.ai/get-started/devin-intro
- Devin deployment: https://docs.devin.ai/enterprise/deploy
- Ollama tool calling: https://docs.ollama.com/capabilities/tool-calling
- Ollama OpenAI compatibility: https://docs.ollama.com/api/openai-compatibility
- Gemma 4: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- Gemma models: https://ai.google.dev/gemma/docs
- Qwen3: https://qwenlm.github.io/blog/qwen3/
- Phi family: https://azure.microsoft.com/products/phi/
- YOLO docs: https://docs.ultralytics.com/
- ML Kit Pose Detection: https://developers.google.com/ml-kit/vision/pose-detection
- SQLite FTS5: https://sqlite.org/fts5.html
- pgvector: https://github.com/pgvector/pgvector
- Qdrant overview: https://qdrant.tech/documentation/overview/

## Conclusao Final

Se eu estivesse a desenhar o seu agente local hoje, eu faria assim:

1. Python
2. Ollama
3. Qwen3 8B ou 14B para o nucleo
4. SQLite no MVP
5. PostgreSQL + pgvector quando crescer
6. Whisper para voz
7. YOLO + pose estimation para visao e movimento
8. MCP oficial em Python para integrar ferramentas reutilizaveis
9. shell e browser sempre com guardrails e preferencialmente sandbox


