@echo off
REM Deploy to GitHub
REM This pushes your code to GitHub so Railway can deploy it

echo.
echo =====================================
echo Deal Intelligence - Deploy to GitHub
echo =====================================
echo.

cd /d "%~dp0"

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed
echo.

REM Initialize Git if needed
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Add files
echo Adding files to Git...
git add .

REM Commit
echo Committing files...
git commit -m "Initial commit: Deal Intelligence platform"

echo.
echo =====================================
echo IMPORTANT: Create GitHub Repository
echo =====================================
echo.
echo Before continuing, you must create a repository on GitHub:
echo 1. Go to https://github.com/new
echo 2. Repository name: deal-intelligence
echo 3. Choose "Public"
echo 4. Click "Create repository"
echo.

set /p username="Enter your GitHub username (kccheah): "
if "%username%"=="" set username=kccheah

echo.
echo Connecting to GitHub...

REM Set remote
git remote remove origin 2>nul
git remote add origin https://github.com/%username%/deal-intelligence.git

REM Set branch
git branch -M main

REM Push
echo Pushing to GitHub...
echo (You may be prompted to authenticate)
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =====================================
    echo SUCCESS! Code pushed to GitHub
    echo =====================================
    echo.
    echo Your repository: https://github.com/%username%/deal-intelligence
    echo.
    echo Next: Go to https://railway.app
    echo 1. Sign up with GitHub
    echo 2. Create new project
    echo 3. Deploy from GitHub repo
    echo 4. Select deal-intelligence
    echo 5. Click Deploy
    echo.
) else (
    echo.
    echo ERROR: Failed to push to GitHub
    echo Check your GitHub credentials and try again
    echo.
)

pause
