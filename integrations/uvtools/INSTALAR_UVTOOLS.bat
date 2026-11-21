@echo off
setlocal EnableExtensions
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uvtools.ps1" -Action install
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" echo [ERRO] Instalacao UVtools interrompida. Consulte runtime\logs\uvtools.
pause
exit /b %ERR%
