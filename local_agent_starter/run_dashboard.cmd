@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente virtual...
  python -m venv .venv
  if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -c "import openai, dotenv" >nul 2>nul
if errorlevel 1 (
  echo Instalando dependencias...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 exit /b 1
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
)

echo.
echo Iniciando Dashboard do Agente Local...
echo Acesse: http://localhost:5173
echo.
echo Pressione Ctrl+C para encerrar.
echo.

".venv\Scripts\python.exe" -m app.main dashboard %*
