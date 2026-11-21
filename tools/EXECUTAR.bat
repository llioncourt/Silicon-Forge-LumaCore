@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist "logs" mkdir "logs"
if "%~1"=="" (
  echo SF - calibracao optica M7 Pro
  echo Arraste para este BAT o PWSZ do CUPOM que foi fatiado no Photon Workshop.
  pause
  exit /b 1
)
set "PYEXE="
if exist "runtime\python\python.exe" set "PYEXE=runtime\python\python.exe"
if not defined PYEXE if exist "runtime\venv\Scripts\python.exe" set "PYEXE=runtime\venv\Scripts\python.exe"
if not defined PYEXE for %%X in (python.exe) do if not defined PYEXE set "PYEXE=%%~$PATH:X"
if not defined PYEXE (
  echo ERRO: Python nao encontrado. Use runtime\python\python.exe
  pause
  exit /b 2
)
set "SFIN=%~f1"
set "SFOUT=%~dpn1_SF_MICRODOSE_TESTE.pwsz"
"%PYEXE%" "%~dp0sf_pwsz.py" inspect "%SFIN%" > "logs\ultima_execucao.log" 2>&1
set "ERR=%ERRORLEVEL%"
type "logs\ultima_execucao.log"
if not "%ERR%"=="0" (
  echo BLOQUEADO. O original nao foi modificado.
  pause
  exit /b %ERR%
)
"%PYEXE%" "%~dp0sf_pwsz.py" patch "%SFIN%" "%SFOUT%" >> "logs\ultima_execucao.log" 2>&1
set "ERR=%ERRORLEVEL%"
type "logs\ultima_execucao.log"
if not "%ERR%"=="0" (echo FALHOU - nao use o resultado.) else (
 echo SAIDA GERADA: "%SFOUT%"
 echo VERIFIQUE NO PHOTON WORKSHOP.
)
pause
exit /b %ERR%
