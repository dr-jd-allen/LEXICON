@echo off
REM LEXICON Local Deployment Script for Windows
REM Deploys LEXICON with local storage and hosting

echo ========================================
echo LEXICON Local Deployment Script
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating local storage directories...
mkdir local-storage\chromadb 2>nul
mkdir local-storage\redis 2>nul
mkdir local-storage\uploads 2>nul
mkdir local-storage\generated-briefs 2>nul
mkdir local-storage\anonymized 2>nul
mkdir local-storage\case-summaries 2>nul
mkdir local-storage\strategic-recommendations 2>nul
mkdir backups\chromadb 2>nul
mkdir backups\daily 2>nul
mkdir logs\nginx 2>nul
mkdir logs\webapp 2>nul
mkdir ssl 2>nul

REM Check for .env file
if not exist .env (
    echo.
    echo WARNING: .env file not found. Creating template...
    (
        echo # LEXICON Environment Variables
        echo ANTHROPIC_API_KEY=your-anthropic-api-key
        echo OPENAI_API_KEY=your-openai-api-key
        echo GOOGLE_API_KEY=your-google-api-key
        echo SERPAPI_API_KEY=your-serpapi-api-key
        echo COURTLISTENER_API_KEY=your-courtlistener-api-key
        echo COURTWHISPERER_API_KEY=your-courtwhisperer-api-key
        echo FIRECRAWL_API_KEY=your-firecrawl-api-key
        echo PUBMED_API_KEY=your-pubmed-api-key
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-here
        echo CHROMA_AUTH_TOKEN=lexicon-secure-token-2024
        echo REDIS_PASSWORD=lexicon-redis-secure-2024
    ) > .env
    echo.
    echo Please edit .env file with your API keys before proceeding.
    pause
    exit /b 1
)

REM Build frontend
echo.
echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..

if not exist frontend\build\index.html (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)

REM Generate self-signed SSL certificates (optional)
if not exist ssl\lexicon.crt (
    echo.
    echo Generating self-signed SSL certificates...
    echo This requires OpenSSL. Skip if not available.
    REM Uncomment if OpenSSL is available:
    REM openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl\lexicon.key -out ssl\lexicon.crt -subj "/C=US/ST=State/L=City/O=LEXICON/CN=localhost"
)

REM Stop existing containers
echo.
echo Stopping existing containers...
docker-compose -f docker-compose-local.yml down

REM Build and start services
echo.
echo Building and starting LEXICON services...
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml up -d

REM Wait for services to start
echo.
echo Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service health
echo.
echo Checking service health...
docker ps --format "table {{.Names}}\t{{.Status}}"

REM Create cron job for backups in Alpine container
echo.
echo Setting up automated backups...
docker exec lexicon-backup-local sh -c "echo '0 2 * * * /scripts/backup.sh' | crontab -"

REM Display access information
echo.
echo ========================================
echo LEXICON is now running locally!
echo ========================================
echo.
echo Access Points:
echo - Web Interface: http://localhost
echo - API Gateway: http://localhost:8000
echo - ChromaDB: http://localhost:8100
echo - File Server: http://localhost:8080/files
echo.
echo Local Storage Locations:
echo - Uploads: %CD%\local-storage\uploads
echo - Generated Briefs: %CD%\local-storage\generated-briefs
echo - Backups: %CD%\backups
echo.
echo Management Commands:
echo - View logs: docker-compose -f docker-compose-local.yml logs -f
echo - Stop services: docker-compose -f docker-compose-local.yml down
echo - Backup now: docker exec lexicon-backup-local /scripts/backup.sh
echo - Restore: docker exec lexicon-backup-local /scripts/restore.sh [backup-file]
echo.
echo ========================================
pause