"""Dashboard web para o agente local."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent import LocalAgent
from .config import Settings
from .tools import ToolRegistry


class DashboardServer:
    """Servidor HTTP simples para o dashboard do agente."""

    def __init__(self, settings: Settings, tools: ToolRegistry, agent: LocalAgent) -> None:
        self.settings = settings
        self.tools = tools
        self.agent = agent

    def get_dashboard_html(self) -> str:
        """Retorna o HTML do dashboard."""
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agente Local - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }

        .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-right: 15px;
            font-weight: bold;
        }

        .chat-icon { background: #667eea; color: white; }
        .voice-icon { background: #f093fb; color: white; }
        .image-icon { background: #4facfe; color: white; }
        .monitor-icon { background: #43e97b; color: white; }

        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
        }

        .card-description {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 20px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }

        input[type="text"],
        input[type="number"],
        textarea,
        select {
            flex: 1;
            padding: 10px 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.95rem;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="number"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
            background: #f8f9ff;
        }

        textarea {
            resize: vertical;
            min-height: 80px;
        }

        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }

        .status-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 200px;
            overflow-y: auto;
        }

        .status-ok {
            color: #43e97b;
        }

        .status-error {
            color: #f5576c;
        }

        .loading {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid #667eea;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }

        .info-item {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9rem;
        }

        .info-item-label {
            color: #666;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-item-value {
            color: #333;
            font-weight: 600;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
        }

        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
            font-size: 0.9rem;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .tab-button {
            flex: 1;
            min-width: 100px;
            padding: 10px;
            background: #f0f0f0;
            border: 2px solid transparent;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .tab-button.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .response-preview {
            background: #f8f9ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 250px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Agente Local</h1>
            <p>Dashboard interativo multimodal</p>
        </header>

        <div class="dashboard-grid">
            <!-- Chat Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon chat-icon">💬</div>
                    <div class="card-title">Chat</div>
                </div>
                <p class="card-description">Envie perguntas ao agente e receba respostas inteligentes.</p>
                <textarea id="chatInput" placeholder="Escreva sua pergunta aqui..."></textarea>
                <div class="input-group" style="margin-top: 15px;">
                    <button class="btn-primary" onclick="sendChat()">Enviar</button>
                </div>
                <div id="chatStatus" class="status-box" style="display:none;"></div>
            </div>

            <!-- Voice Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon voice-icon">🎤</div>
                    <div class="card-title">Voz</div>
                </div>
                <p class="card-description">Grave áudio do microfone e transcreva automaticamente.</p>
                <div class="input-group">
                    <input type="number" id="recordSeconds" placeholder="Segundos (ex: 5)" value="5" min="1" max="60">
                </div>
                <button class="btn-primary" onclick="startRecording()">🎙️ Gravar Áudio</button>
                <div id="voiceStatus" class="status-box" style="display:none;"></div>
            </div>

            <!-- Image Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon image-icon">🖼️</div>
                    <div class="card-title">Gerar Imagem</div>
                </div>
                <p class="card-description">Crie imagens PNG usando prompts de texto.</p>
                <textarea id="imagePrompt" placeholder="Descreva a imagem desejada..."></textarea>
                <div class="input-group" style="margin-top: 15px;">
                    <input type="text" id="imageName" placeholder="Nome do arquivo (ex: imagem.png)">
                </div>
                <button class="btn-primary" onclick="generateImage()">Gerar</button>
                <div id="imageStatus" class="status-box" style="display:none;"></div>
            </div>

            <!-- Monitor Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon monitor-icon">📊</div>
                    <div class="card-title">Monitorar</div>
                </div>
                <p class="card-description">Analise as mudanças no workspace.</p>
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="monitorWorkspace('view')">Visualizar</button>
                    <button class="tab-button" onclick="monitorWorkspace('reset')">Resetar</button>
                </div>
                <div id="monitorStatus" class="status-box" style="display:none;"></div>
            </div>

            <!-- Diagnostics Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: #ffa502; color: white;">🔧</div>
                    <div class="card-title">Diagnóstico</div>
                </div>
                <p class="card-description">Verifique o estado do ambiente e dependências.</p>
                <button class="btn-primary" onclick="runDiagnostics()">Executar Diagnóstico</button>
                <div id="diagnosticsStatus" class="status-box" style="display:none;"></div>
            </div>

            <!-- Info Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: #667eea; color: white;">ℹ️</div>
                    <div class="card-title">Informações</div>
                </div>
                <p class="card-description">Detalhes de configuração do agente.</p>
                <div class="info-grid" id="infoContainer"></div>
                <button class="btn-secondary" onclick="loadInfo()">Atualizar</button>
            </div>
        </div>

        <footer>
            <p>© 2026 Local Agent - Dashboard v1.0</p>
        </footer>
    </div>

    <script>
        const API_BASE = 'http://localhost:5173/api';

        async function sendRequest(endpoint, method = 'POST', data = null) {
            try {
                const options = {
                    method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (data) options.body = JSON.stringify(data);

                const response = await fetch(`${API_BASE}${endpoint}`, options);
                return await response.json();
            } catch (error) {
                return { ok: false, error: error.message };
            }
        }

        async function sendChat() {
            const input = document.getElementById('chatInput');
            const status = document.getElementById('chatStatus');
            const text = input.value.trim();

            if (!text) return;

            input.disabled = true;
            status.innerHTML = '<span class="loading"></span> Processando...';
            status.style.display = 'block';

            const result = await sendRequest('/chat', 'POST', { prompt: text });

            if (result.ok) {
                status.innerHTML = `<span class="status-ok">✓ Resposta:</span>\\n${result.response}`;
                input.value = '';
            } else {
                status.innerHTML = `<span class="status-error">✗ Erro: ${result.error || 'Desconhecido'}</span>`;
            }

            input.disabled = false;
        }

        async function startRecording() {
            const seconds = parseInt(document.getElementById('recordSeconds').value) || 5;
            const status = document.getElementById('voiceStatus');

            status.innerHTML = '<span class="loading"></span> Gravando...';
            status.style.display = 'block';

            const result = await sendRequest('/record', 'POST', { seconds });

            if (result.ok) {
                status.innerHTML = `<span class="status-ok">✓ Gravado:</span>\\n${result.path}\\n\\n<span class="status-ok">Transcrição:</span>\\n${result.transcript}`;
            } else {
                status.innerHTML = `<span class="status-error">✗ Erro: ${result.error || 'Falha ao gravar'}</span>`;
            }
        }

        async function generateImage() {
            const prompt = document.getElementById('imagePrompt').value.trim();
            const name = document.getElementById('imageName').value.trim() || 'image.png';
            const status = document.getElementById('imageStatus');

            if (!prompt) {
                status.innerHTML = '<span class="status-error">✗ Digite um prompt</span>';
                status.style.display = 'block';
                return;
            }

            status.innerHTML = '<span class="loading"></span> Gerando imagem...';
            status.style.display = 'block';

            const result = await sendRequest('/image', 'POST', { prompt, output: name });

            if (result.ok) {
                status.innerHTML = `<span class="status-ok">✓ Imagem gerada:</span>\\n${result.path}`;
                document.getElementById('imagePrompt').value = '';
            } else {
                status.innerHTML = `<span class="status-error">✗ Erro: ${result.error || 'Falha ao gerar'}</span>`;
            }
        }

        async function monitorWorkspace(action) {
            const status = document.getElementById('monitorStatus');

            status.innerHTML = '<span class="loading"></span> Processando...';
            status.style.display = 'block';

            const result = await sendRequest('/monitor', 'POST', { reset: action === 'reset' });

            if (result.ok) {
                status.innerHTML = `<span class="status-ok">✓ Resultado:</span>\\n${JSON.stringify(result, null, 2)}`;
            } else {
                status.innerHTML = `<span class="status-error">✗ Erro: ${result.error || 'Desconhecido'}</span>`;
            }
        }

        async function runDiagnostics() {
            const status = document.getElementById('diagnosticsStatus');

            status.innerHTML = '<span class="loading"></span> Executando...';
            status.style.display = 'block';

            const result = await sendRequest('/doctor', 'GET');

            if (result.ok) {
                let html = '<span class="status-ok">✓ Ambiente OK</span>\\n\\n';
                if (result.checks) {
                    result.checks.forEach(check => {
                        const icon = check.ok ? '✓' : '✗';
                        const color = check.ok ? 'status-ok' : 'status-error';
                        html += `<span class="${color}">${icon} ${check.name}: ${check.details}</span>\\n`;
                    });
                }
                status.innerHTML = html;
            } else {
                status.innerHTML = `<span class="status-error">✗ Erro: ${result.error || 'Desconhecido'}</span>`;
            }
        }

        async function loadInfo() {
            const container = document.getElementById('infoContainer');
            const result = await sendRequest('/info', 'GET');

            if (result.ok && result.info) {
                const info = result.info;
                container.innerHTML = `
                    <div class="info-item">
                        <div class="info-item-label">Modelo</div>
                        <div class="info-item-value">${info.model || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-item-label">URL Base</div>
                        <div class="info-item-value">${info.base_url || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-item-label">Workspace</div>
                        <div class="info-item-value">${info.workspace || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-item-label">Permissões</div>
                        <div class="info-item-value">${info.allow_write ? 'Escrita ✓' : 'Apenas leitura'}</div>
                    </div>
                `;
            }
        }

        // Carregar informações ao abrir
        window.addEventListener('load', loadInfo);
    </script>
</body>
</html>"""

    def start_server(self, host: str = "localhost", port: int = 5173) -> None:
        """Inicia o servidor HTTP."""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading

            handler = self._create_handler()
            server = HTTPServer((host, port), handler)

            print(f"Dashboard disponível em: http://{host}:{port}")

            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")

    def _create_handler(self) -> type:
        """Cria o handler HTTP."""
        tools = self.tools
        agent = self.agent
        settings = self.settings
        dashboard_html = self.get_dashboard_html()

        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(dashboard_html.encode("utf-8"))
                elif self.path == "/api/info":
                    self.send_json(
                        {
                            "ok": True,
                            "info": {
                                "model": settings.model,
                                "base_url": settings.base_url,
                                "workspace": str(settings.workspace),
                                "allow_write": settings.allow_write,
                            },
                        }
                    )
                elif self.path == "/api/doctor":
                    self.send_json(tools.diagnose())
                else:
                    self.send_error(404)

            def do_POST(self) -> None:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")

                try:
                    data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    data = {}

                if self.path == "/api/chat":
                    response = self._handle_chat(data)
                elif self.path == "/api/record":
                    response = self._handle_record(data)
                elif self.path == "/api/image":
                    response = self._handle_image(data)
                elif self.path == "/api/monitor":
                    response = self._handle_monitor(data)
                else:
                    response = {"ok": False, "error": "Endpoint não encontrado"}

                self.send_json(response)

            def _handle_chat(self, data: dict[str, Any]) -> dict[str, Any]:
                prompt = data.get("prompt", "").strip()
                if not prompt:
                    return {"ok": False, "error": "Prompt vazio"}
                try:
                    response = agent.ask(prompt)
                    return {"ok": True, "response": response}
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            def _handle_record(self, data: dict[str, Any]) -> dict[str, Any]:
                seconds = data.get("seconds", 5)
                try:
                    result = tools.record_microphone(seconds=seconds)
                    if result.get("ok"):
                        transcript = tools.transcribe_audio_file(result["path"])
                        return {
                            "ok": True,
                            "path": result["path"],
                            "transcript": transcript.get("text", ""),
                        }
                    return result
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            def _handle_image(self, data: dict[str, Any]) -> dict[str, Any]:
                prompt = data.get("prompt", "").strip()
                output = data.get("output", "image.png")
                try:
                    result = tools.generate_image(prompt=prompt, output_path=output)
                    return result
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            def _handle_monitor(self, data: dict[str, Any]) -> dict[str, Any]:
                reset = data.get("reset", False)
                try:
                    result = tools.monitor_workspace(reset=reset)
                    return result
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            def send_json(self, data: dict[str, Any]) -> None:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

            def log_message(self, format: str, *args: Any) -> None:
                pass  # Suprime logs

        return DashboardHandler
