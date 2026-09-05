# Deploy to GitHub - Simple Script
# Usage: powershell -ExecutionPolicy Bypass -File deploy-to-github.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deal Intelligence - GitHub Deploy" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Git is not installed." -ForegroundColor Red
    Write-Host "  Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green

# Navigate to project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host ""
Write-Host "Project directory: $projectDir" -ForegroundColor Cyan
Write-Host ""

# Initialize Git repo
if (Test-Path ".git") {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository created" -ForegroundColor Green
}

# Add all files
Write-Host ""
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files staged" -ForegroundColor Green

# Check if there are changes to commit
$gitStatus = git status --porcelain
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "✓ No changes to commit" -ForegroundColor Green
} else {
    Write-Host "Committing files..." -ForegroundColor Yellow
    git commit -m "Initial commit: Deal Intelligence platform - ready for Railway deployment"
    Write-Host "✓ Files committed" -ForegroundColor Green
}

# Get username
Write-Host ""
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Important: GitHub Repository Setup" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Before pushing, you must create a repository on GitHub:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Name it: deal-intelligence" -ForegroundColor White
Write-Host "3. Choose 'Public' (free tier)" -ForegroundColor White
Write-Host "4. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$username = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "✗ Username cannot be empty" -ForegroundColor Red
    exit 1
}

# Add remote
Write-Host ""
Write-Host "Connecting to GitHub..." -ForegroundColor Yellow
$repoUrl = "https://github.com/$username/deal-intelligence.git"

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Updating existing remote..." -ForegroundColor Yellow
    git remote set-url origin $repoUrl
} else {
    Write-Host "Adding new remote..." -ForegroundColor Yellow
    git remote add origin $repoUrl
}

# Set branch to main
git branch -M main
Write-Host "✓ Branch set to 'main'" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "(You may be prompted to authenticate with GitHub)" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "✅ Successfully pushed to GitHub" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository is now live at:" -ForegroundColor Cyan
    Write-Host "  https://github.com/$username/deal-intelligence" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Go to https://railway.app" -ForegroundColor White
    Write-Host "2. Sign up (use GitHub to connect)" -ForegroundColor White
    Write-Host "3. Create new project" -ForegroundColor White
    Write-Host "4. Select 'Deploy from GitHub'" -ForegroundColor White
    Write-Host "5. Choose 'deal-intelligence' repository" -ForegroundColor White
    Write-Host "6. Click Deploy" -ForegroundColor White
    Write-Host ""
    Write-Host "Your API will be live in 5-10 minutes!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✗ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "  Check your authentication and try again" -ForegroundColor Yellow
    exit 1
}

pause
