@echo off
setlocal enabledelayedexpansion
REM LEXICON Docker Image Pre-Build Script
REM Pre-builds and caches Docker images for faster startup

color 0A
cls

echo ================================================
echo      LEXICON DOCKER IMAGE PRE-BUILD
echo ================================================
echo.
echo This will pre-build Docker images to speed up
echo subsequent test runs and deployments.
echo.

REM Check if Docker is running
docker info >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Pull base images
echo Step 1/3: Pulling base images...
echo ========================================
set "IMAGES=nginx:alpine chromadb/chroma:latest redis:7-alpine alpine:latest halverneus/static-file-server:latest"

for %%i in (!IMAGES!) do (
    echo Pulling %%i...
    docker pull %%i
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Failed to pull %%i
    )
)

REM Build webapp image if Dockerfile exists
echo.
echo Step 2/3: Building webapp image...
echo ========================================
if exist "Dockerfile" (
    echo Building lexicon-webapp:latest...
    docker build -t lexicon-webapp:latest .
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to build webapp image!
        pause
        exit /b 1
    )
) else (
    echo WARNING: Dockerfile not found, skipping webapp build
)

REM Pre-create volumes
echo.
echo Step 3/3: Pre-creating Docker volumes...
echo ========================================
docker volume create lexicon-local-storage >nul 2>&1
docker volume create lexicon-backups >nul 2>&1
docker volume create lexicon-logs >nul 2>&1

REM Display results
echo.
echo ================================================
echo         PRE-BUILD COMPLETE
echo ================================================
echo.
echo The following images are now cached locally:
docker images | findstr /C:"nginx" /C:"chroma" /C:"redis" /C:"lexicon"
echo.
echo Docker volumes created:
docker volume ls | findstr lexicon
echo.
echo Your Docker environment is now optimized for
echo faster LEXICON startup times!
echo.
pause