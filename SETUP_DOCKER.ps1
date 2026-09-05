# ============================================================================
# DEAL INTELLIGENCE - DOCKER SETUP SCRIPT FOR WINDOWS (PowerShell)
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "DEAL INTELLIGENCE PLATFORM - DOCKER SETUP" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found" -ForegroundColor Yellow
    Write-Host "Copying from .env template..." -ForegroundColor Yellow
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host "✓ Created .env from template" -ForegroundColor Green
    } else {
        Write-Host "ERROR: .env.template not found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Starting Docker Services" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "This will start PostgreSQL, API server, and Redis..." -ForegroundColor White
Write-Host ""

docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start Docker services" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Docker services started" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Waiting for Services to Initialize (10 seconds)" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Start-Sleep -Seconds 10
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Testing API Health" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$maxRetries = 10
$retryCount = 0

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction Stop
        Write-Host "✓ API is healthy and running!" -ForegroundColor Green
        break
    } catch {
        $retryCount++
        Write-Host "Waiting for API to start (attempt $retryCount/$maxRetries)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "SUCCESS! Your platform is running" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "API Health:        http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:8000/docs in your browser" -ForegroundColor White
Write-Host "2. Test the signup endpoint with sample data" -ForegroundColor White
Write-Host "3. Check the logs: docker-compose logs -f api" -ForegroundColor White
Write-Host ""
Write-Host "TO STOP SERVICES:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Gray
Write-Host ""
Write-Host "TO VIEW LOGS:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f api" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to continue"
