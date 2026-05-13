from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", value.lower())
    return "-".join(tokens) or "site"


def _site_files(title: str, brief: str) -> dict[str, str]:
    safe_title = escape(title.strip() or "Novo site")
    safe_brief = escape(brief.strip() or "Site gerado pelo agente local.")

    html = f"""<!DOCTYPE html>
<html lang="pt">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_title}</title>
    <meta name="description" content="{safe_brief}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div class="background-glow"></div>
    <header class="hero">
      <nav class="topbar">
        <span class="brand">{safe_title}</span>
        <a class="cta-link" href="#contacto">Falar agora</a>
      </nav>

      <section class="hero-copy reveal">
        <p class="eyebrow">Site criado pelo agente local</p>
        <h1>{safe_title}</h1>
        <p class="lead">{safe_brief}</p>
        <div class="hero-actions">
          <a class="button primary" href="#servicos">Explorar</a>
          <a class="button secondary" href="#processo">Ver processo</a>
        </div>
      </section>
    </header>

    <main>
      <section class="grid-section reveal" id="servicos">
        <article class="card">
          <h2>Leitura e analise</h2>
          <p>Organiza informacao, interpreta pedidos e transforma ideias em entregas praticas.</p>
        </article>
        <article class="card">
          <h2>Criacao rapida</h2>
          <p>Gera paginas, conteudo, automacoes e estruturas de projeto prontas para evoluir.</p>
        </article>
        <article class="card">
          <h2>Operacao controlada</h2>
          <p>Executa acoes de forma observavel, com monitoramento e guardrails configuraveis.</p>
        </article>
      </section>

      <section class="story reveal" id="processo">
        <div>
          <p class="eyebrow">Como funciona</p>
          <h2>Um fluxo simples para sair da ideia e chegar na execucao.</h2>
        </div>
        <ol class="timeline">
          <li>Receber o pedido e identificar o objetivo.</li>
          <li>Ler, analisar e reunir contexto real.</li>
          <li>Criar artefactos ou executar tarefas no workspace.</li>
          <li>Monitorar o resultado e iterar com seguranca.</li>
        </ol>
      </section>

      <section class="banner reveal" id="contacto">
        <p class="eyebrow">Proximo passo</p>
        <h2>Este projeto ja pode servir como base para um assistente operacional local.</h2>
        <a class="button primary" href="mailto:contato@example.com">Definir integracoes</a>
      </section>
    </main>

    <footer class="footer">
      <span>{safe_title}</span>
      <span id="year"></span>
    </footer>

    <script src="./script.js"></script>
  </body>
</html>
"""

    css = """* {
  box-sizing: border-box;
}

:root {
  --bg: #06131c;
  --bg-soft: #102635;
  --panel: rgba(10, 27, 38, 0.78);
  --text: #f4f5ef;
  --muted: #b8c3c8;
  --line: rgba(255, 255, 255, 0.12);
  --accent: #3dd6b5;
  --accent-strong: #16a085;
  --shadow: 0 30px 80px rgba(0, 0, 0, 0.28);
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(61, 214, 181, 0.15), transparent 35%),
    linear-gradient(160deg, var(--bg) 0%, #071a25 55%, #0a2433 100%);
  color: var(--text);
  font-family: "Space Grotesk", sans-serif;
}

.background-glow {
  position: fixed;
  inset: 2rem auto auto 55%;
  width: 22rem;
  height: 22rem;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(61, 214, 181, 0.22), transparent 70%);
  filter: blur(12px);
  pointer-events: none;
}

.hero,
main,
.footer {
  width: min(1120px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  padding: 1.5rem 0 3rem;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.brand,
.footer span:first-child {
  font-family: "Fraunces", serif;
  font-size: 1.1rem;
  letter-spacing: 0.04em;
}

.cta-link {
  color: var(--text);
  text-decoration: none;
  border-bottom: 1px solid transparent;
}

.cta-link:hover {
  border-color: var(--accent);
}

.hero-copy {
  padding: 5.5rem 0 4rem;
  max-width: 50rem;
}

.eyebrow {
  margin: 0 0 1rem;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.78rem;
}

h1,
h2 {
  margin: 0;
  font-family: "Fraunces", serif;
  line-height: 0.96;
}

h1 {
  font-size: clamp(3rem, 9vw, 6.8rem);
  max-width: 10ch;
}

h2 {
  font-size: clamp(2rem, 4vw, 3.6rem);
}

.lead {
  max-width: 42rem;
  margin: 1.5rem 0 0;
  color: var(--muted);
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  line-height: 1.75;
}

.hero-actions,
.button {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.hero-actions {
  margin-top: 2rem;
}

.button {
  align-items: center;
  justify-content: center;
  min-width: 10rem;
  padding: 0.95rem 1.3rem;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 700;
  transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
}

.button:hover {
  transform: translateY(-2px);
}

.button.primary {
  background: linear-gradient(135deg, var(--accent) 0%, #61f7cb 100%);
  color: #041218;
}

.button.secondary {
  color: var(--text);
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.04);
}

.grid-section {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 2rem auto 5rem;
}

.card,
.story,
.banner {
  background: var(--panel);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.card {
  padding: 1.5rem;
  border-radius: 1.6rem;
}

.card h2 {
  font-size: 1.6rem;
  margin-bottom: 0.9rem;
}

.card p,
.timeline li {
  color: var(--muted);
  line-height: 1.7;
}

.story,
.banner {
  border-radius: 2rem;
}

.story {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 2rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.timeline {
  margin: 0;
  padding-left: 1.2rem;
}

.timeline li + li {
  margin-top: 1rem;
}

.banner {
  padding: 2rem;
  margin-bottom: 4rem;
}

.banner h2 {
  max-width: 16ch;
  margin-bottom: 1.3rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0 0 2rem;
  color: var(--muted);
}

.reveal {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 500ms ease, transform 500ms ease;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 900px) {
  .grid-section,
  .story {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-copy {
    padding-top: 4rem;
  }

  .topbar,
  .footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .button {
    width: 100%;
  }
}
"""

    script = """const revealItems = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.18 });

revealItems.forEach((item) => observer.observe(item));

document.getElementById('year').textContent = new Date().getFullYear();
"""

    readme = f"""# {safe_title}

Site gerado pelo agente local.

## Ficheiros

- `index.html`: estrutura principal
- `styles.css`: identidade visual
- `script.js`: pequenas interacoes

## Como abrir

Abra `index.html` diretamente no navegador ou use:

```powershell
python -m http.server 8000
```
"""

    return {
        "index.html": html,
        "styles.css": css,
        "script.js": script,
        "README.md": readme,
    }


def create_site_project(
    workspace: Path,
    output_root: Path,
    project_name: str,
    title: str,
    brief: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    slug = slugify(project_name or title)
    project_dir = output_root / slug
    if project_dir.exists() and any(project_dir.iterdir()) and not overwrite:
        return {
            "ok": False,
            "error": "A pasta do site ja existe e nao esta vazia.",
            "path": str(project_dir.relative_to(workspace)).replace("\\", "/"),
        }

    project_dir.mkdir(parents=True, exist_ok=True)
    created_files: list[str] = []
    for filename, content in _site_files(title=title, brief=brief).items():
        target = project_dir / filename
        target.write_text(content, encoding="utf-8")
        created_files.append(str(target.relative_to(workspace)).replace("\\", "/"))

    return {
        "ok": True,
        "project": slug,
        "path": str(project_dir.relative_to(workspace)).replace("\\", "/"),
        "files": created_files,
    }
