@echo off
setlocal
cd /d "%~dp0"
if not exist "input_png" mkdir "input_png"
if not exist "output_png" mkdir "output_png"
if not exist "runtime\logs" mkdir "runtime\logs"
if exist "runtime\venv\Scripts\python.exe" goto RUN
where py >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado. Use Python portatil local.
  pause
  exit /b 1
)
py -3 -m venv "%~dp0runtime\venv"
if errorlevel 1 exit /b 1
"%~dp0runtime\venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
  echo ERRO: dependencia local indisponivel.
  pause
  exit /b 1
)
:RUN
if not exist "input_png\*.png" (
  echo Exporte fatias PNG para input_png. NAO gera .pwsz imprimivel.
  pause
  exit /b 2
)
"%~dp0runtime\venv\Scripts\python.exe" "%~dp0run_local.py" > "%~dp0runtime\logs\run.log" 2>&1
set CODE=%ERRORLEVEL%
type "%~dp0runtime\logs\run.log"
pause
exit /b %CODE%
