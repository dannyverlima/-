@echo off
setlocal
title Relatorio de Agentes IA
color 0A
if not exist "%~dp0RELATORIO_AGENTES_IA.md" (
  echo Nao encontrei o ficheiro RELATORIO_AGENTES_IA.md
  pause
  exit /b 1
)
type "%~dp0RELATORIO_AGENTES_IA.md" | more
echo.
echo Fim do relatorio.
pause
endlocal
