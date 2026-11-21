@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if "%~1"=="" (
 echo.
 echo SILICON FORGE LUMACORE ^| AUDITORIA LEITURA SOMENTE
 echo Arraste um arquivo .pwsz para este BAT.
 echo Originais nunca sao refatiados, reparados ou sobrescritos.
 pause
 exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uvtools.ps1" -Action issues -InputFile "%~f1"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" echo [ERRO] Auditoria nao concluida. Confira os logs locais.
pause
exit /b %ERR%
