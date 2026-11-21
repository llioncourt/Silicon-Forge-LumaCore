@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if "%~2"=="" (
 echo.
 echo Uso: COMPARAR_PWSZ.bat "original.pwsz" "modificado.pwsz"
 echo Para arrastar arquivos, utilize CMD ou atalho com dois argumentos.
 pause
 exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uvtools.ps1" -Action compare -InputFile "%~f1" -OtherFile "%~f2"
set "ERR=%ERRORLEVEL%"
pause
exit /b %ERR%
