@echo off
REM LEXICON Installer Build Script
REM Packages everything into a single executable

echo ========================================
echo LEXICON Installer Build Script
echo ========================================
echo.

REM Check prerequisites
where /q npm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm not found. Please install Node.js
    pause
    exit /b 1
)

where /q docker
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker not found. Please install Docker Desktop
    pause
    exit /b 1
)

REM Create build directories
echo Creating build directories...
mkdir build 2>nul
mkdir build\app 2>nul
mkdir build\assets 2>nul
mkdir installer 2>nul
mkdir launcher\assets 2>nul

REM Build frontend
echo.
echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..

if not exist frontend\build\index.html (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)

REM Copy frontend build
echo Copying frontend files...
xcopy /E /Y /Q frontend\build build\app\frontend\

REM Build Electron launcher
echo.
echo Building Electron launcher...
cd launcher
call npm install
call npm run build-win
cd ..

if not exist launcher\dist\LEXICON-Setup-1.0.0.exe (
    echo ERROR: Electron build failed
    pause
    exit /b 1
)

REM Prepare application bundle
echo.
echo Preparing application bundle...

REM Copy backend files
xcopy /Y *.py build\app\
xcopy /Y requirements*.txt build\app\
xcopy /Y docker-compose*.yml build\app\
xcopy /Y *.conf build\app\
xcopy /Y *.md build\app\
xcopy /Y .env.example build\app\.env

REM Copy Docker configurations
xcopy /E /Y /Q docker build\app\docker\

REM Copy scripts
xcopy /E /Y /Q backup-scripts build\app\backup-scripts\
copy deploy-local.bat build\app\
copy deploy-local.ps1 build\app\

REM Copy corpus (sample only for demo)
echo Copying sample corpus...
mkdir build\app\tbi-corpus\sample 2>nul
xcopy /Y tbi-corpus\processed\*.json build\app\tbi-corpus\sample\ /S

REM Create assets
echo.
echo Creating installer assets...

REM Generate icon if not exists
if not exist launcher\assets\icon.ico (
    echo WARNING: icon.ico not found, using default
    REM Create a simple icon or copy from somewhere
)

REM Create Quick Start PDF from Markdown
echo Converting Quick Start Guide to PDF...
REM This requires pandoc or similar tool
REM For now, just copy the markdown
copy QUICK_START_GUIDE.md "build\Quick Start Guide.txt"

REM Package with NSIS
echo.
echo Building NSIS installer...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    "C:\Program Files (x86)\NSIS\makensis.exe" installer\LEXICON-Installer.nsi
) else if exist "C:\Program Files\NSIS\makensis.exe" (
    "C:\Program Files\NSIS\makensis.exe" installer\LEXICON-Installer.nsi
) else (
    echo ERROR: NSIS not found. Please install NSIS.
    echo Download from: https://nsis.sourceforge.io/
    pause
    exit /b 1
)

REM Create portable version
echo.
echo Creating portable version...
mkdir dist 2>nul
powershell Compress-Archive -Path "build\*" -DestinationPath "dist\LEXICON-Portable-v1.0.zip" -Force

REM Final output
echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Outputs:
echo - Installer: LEXICON-Setup-v1.0.exe
echo - Portable: dist\LEXICON-Portable-v1.0.zip
echo - Electron: launcher\dist\LEXICON-Setup-1.0.0.exe
echo.
echo Next steps:
echo 1. Test the installer on a clean system
echo 2. Code sign the executables
echo 3. Upload to distribution server
echo.
pause