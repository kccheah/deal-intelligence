@echo off
REM Deal Intelligence - Docker Auto Start
REM Run this file to start all services

echo.
echo =====================================
echo Deal Intelligence - Starting Docker
echo =====================================
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo Creating .env from template...
    copy "config\.env.template" ".env"
    echo.
    echo IMPORTANT: Edit .env and add your API keys:
    echo   - ANTHROPIC_API_KEY from https://console.anthropic.com
    echo   - NEWSAPI_KEY from https://newsapi.org
    echo.
    echo Then run this file again.
    pause
    exit /b
)

echo Starting Docker services...
docker-compose -f devops\docker-compose.yml down -v 2>nul
docker-compose -f devops\docker-compose.yml up -d

echo.
echo Waiting 30 seconds for services to start...
timeout /t 30 /nobreak

echo.
echo Checking if API is ready...
curl http://localhost:8000/health

echo.
echo =====================================
echo SETUP COMPLETE
echo =====================================
echo.
echo API is running at: http://localhost:8000/docs
echo.
echo Open this in your browser to test the API.
echo.
pause
