@echo off
REM LEXICON One-Click Launcher
REM Simple double-click solution for lawyers

title LEXICON Legal AI System

REM Hide the command window
if not "%1"=="hidden" (
    start /b "" "%~0" hidden
    exit /b
)

REM Check if already running
tasklist /FI "WINDOWTITLE eq LEXICON Legal AI System" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    msg "%username%" "LEXICON is already running. Check your system tray."
    exit /b
)

REM Start minimized PowerShell launcher
powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0launcher\start-lexicon.ps1"

exit /b