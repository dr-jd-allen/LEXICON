@echo off
REM LEXICON Pre-Flight Check Runner
REM Run this BEFORE first installation

color 0B
cls

echo ===============================================
echo         LEXICON PRE-FLIGHT CHECK
echo ===============================================
echo.
echo This will verify your system is ready for LEXICON
echo.
pause

powershell.exe -ExecutionPolicy Bypass -File "%~dp0pre-flight-check.ps1"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo Pre-flight check failed. Please fix errors above.
) else (
    color 0A
    echo.
    echo Pre-flight check passed! You can now run LEXICON.bat
)

pause