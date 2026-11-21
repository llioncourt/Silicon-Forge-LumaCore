@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if "%~1"=="" (
 powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uvtools.ps1" -Action gui
) else (
 powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uvtools.ps1" -Action gui -InputFile "%~f1"
)
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
 echo [ERRO] Nao foi possivel iniciar UVtools. Consulte runtime\logs\uvtools.
 pause
)
exit /b %ERR%
