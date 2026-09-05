# Deal Intelligence Platform - Docker Automated Setup
# This script sets up everything needed to run the API locally via Docker
# Just run: powershell -ExecutionPolicy Bypass -File setup-docker.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deal Intelligence - Docker Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "  Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Get the script directory (where iCloud drive is)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

Write-Host ""
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Setting up environment variables..." -ForegroundColor Yellow

$envFile = "$projectRoot\.env"
$envTemplate = "$projectRoot\config\.env.template"

if (Test-Path $envFile) {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
} else {
    if (Test-Path $envTemplate) {
        Copy-Item $envTemplate $envFile
        Write-Host "✓ Created .env from template" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Edit .env file and add your API keys:" -ForegroundColor Yellow
        Write-Host "   - ANTHROPIC_API_KEY: Get from https://console.anthropic.com" -ForegroundColor White
        Write-Host "   - NEWSAPI_KEY: Get from https://newsapi.org" -ForegroundColor White
        Write-Host ""
        Write-Host "Then run this script again." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "✗ Template file not found at $envTemplate" -ForegroundColor Red
        exit 1
    }
}

# Verify required API keys are set
Write-Host ""
Write-Host "Checking API keys in .env..." -ForegroundColor Yellow

$envContent = Get-Content $envFile
$hasAnthropic = $envContent | Select-String "ANTHROPIC_API_KEY" | Select-String -NotMatch "^#"
$hasNewsAPI = $envContent | Select-String "NEWSAPI_KEY" | Select-String -NotMatch "^#"

if (-not $hasAnthropic -or -not $hasNewsAPI) {
    Write-Host "✗ API keys not set in .env file" -ForegroundColor Red
    Write-Host "  Edit: $envFile" -ForegroundColor Yellow
    Write-Host "  Add your Anthropic and NewsAPI keys, then run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ API keys configured" -ForegroundColor Green

# Stop any existing containers
Write-Host ""
Write-Host "Cleaning up old containers..." -ForegroundColor Yellow
try {
    docker-compose -f "$projectRoot\devops\docker-compose.yml" down -v 2>$null
    Write-Host "✓ Old containers removed" -ForegroundColor Green
} catch {
    Write-Host "✓ No old containers to remove" -ForegroundColor Green
}

# Start Docker services
Write-Host ""
Write-Host "Starting Docker services..." -ForegroundColor Yellow
Write-Host "  - PostgreSQL database" -ForegroundColor Cyan
Write-Host "  - FastAPI server" -ForegroundColor Cyan
Write-Host "  - Redis cache" -ForegroundColor Cyan
Write-Host ""

# Use absolute path to docker-compose file
$dockerComposeFile = "$projectRoot\devops\docker-compose.yml"

if (-not (Test-Path $dockerComposeFile)) {
    Write-Host "✗ docker-compose.yml not found at $dockerComposeFile" -ForegroundColor Red
    exit 1
}

# Start services with proper working directory
Push-Location $projectRoot
try {
    docker-compose -f $dockerComposeFile up -d
    Write-Host "✓ Services started" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to start Docker services" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

# Wait for services to be ready
Write-Host ""
Write-Host "Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if API is responding
Write-Host ""
Write-Host "Verifying API is running..." -ForegroundColor Yellow

$maxAttempts = 5
$attempt = 0
$apiReady = $false

while ($attempt -lt $maxAttempts -and -not $apiReady) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $apiReady = $true
            Write-Host "✓ API is responding at http://localhost:8000" -ForegroundColor Green
        }
    } catch {
        if ($attempt -lt $maxAttempts) {
            Write-Host "  Checking again... (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
            Start-Sleep -Seconds 5
        }
    }
}

if (-not $apiReady) {
    Write-Host "✗ API not responding after waiting" -ForegroundColor Red
    Write-Host "  Run: docker-compose logs -f api" -ForegroundColor Yellow
    exit 1
}

# Final summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "✅ SETUP COMPLETE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Deal Intelligence API is now running!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor Cyan
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "   • Database: PostgreSQL on localhost:5432" -ForegroundColor White
Write-Host "   • Redis Cache: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test It:" -ForegroundColor Cyan
Write-Host "   Open browser: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Or run:" -ForegroundColor White
Write-Host "     curl http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open QUICKSTART.md for API testing examples" -ForegroundColor White
Write-Host "   2. Open http://localhost:8000/docs to try endpoints" -ForegroundColor White
Write-Host "   3. Follow WEEK1_ACTION_PLAN.md for next phase" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To Stop Services:" -ForegroundColor Cyan
Write-Host "   Run: docker-compose down" -ForegroundColor White
Write-Host ""
