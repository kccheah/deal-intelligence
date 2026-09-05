@echo off
REM ============================================================================
REM DEAL INTELLIGENCE - DOCKER SETUP SCRIPT FOR WINDOWS
REM ============================================================================
REM This script sets up and starts the Docker environment
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo DEAL INTELLIGENCE PLATFORM - DOCKER SETUP
echo ============================================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✓ Docker found: & docker --version
echo.

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Copying from .env template...
    if exist .env.template (
        copy .env.template .env
        echo ✓ Created .env from template
    ) else (
        echo ERROR: .env.template not found
        pause
        exit /b 1
    )
)

echo.
echo ============================================================================
echo STEP 1: Starting Docker Services
echo ============================================================================
echo This will start PostgreSQL, API server, and Redis...
echo.

docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)

echo ✓ Docker services started
echo.

REM Wait for services to be healthy
echo ============================================================================
echo STEP 2: Waiting for Services to Initialize (10 seconds)
echo ============================================================================
echo.
timeout /t 10 /nobreak
echo.

REM Check if API is responding
echo ============================================================================
echo STEP 3: Testing API Health
echo ============================================================================
echo.

:retry_health
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ API is healthy and running!
    goto success
) else (
    echo Waiting for API to start...
    timeout /t 3 /nobreak
    goto retry_health
)

:success
echo.
echo ============================================================================
echo SUCCESS! Your platform is running
echo ============================================================================
echo.
echo API Documentation: http://localhost:8000/docs
echo API Health:        http://localhost:8000/health
echo.
echo NEXT STEPS:
echo 1. Open http://localhost:8000/docs in your browser
echo 2. Test the signup endpoint with sample data
echo 3. Check the logs: docker-compose logs -f api
echo.
echo TO STOP SERVICES:
echo   docker-compose down
echo.
echo TO VIEW LOGS:
echo   docker-compose logs -f api
echo.
pause
exit /b 0
