@echo off
echo 🚀 Premium Scraper Deployment Script
echo ==================================

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not initialized. Please run 'git init' first.
    pause
    exit /b 1
)

REM Check if there are uncommitted changes
git status --porcelain > temp_status.txt
if not %errorlevel% equ 0 (
    echo ❌ Failed to check git status
    pause
    exit /b 1
)

for /f %%i in ('type temp_status.txt ^| find /c /v ""') do set changes=%%i
del temp_status.txt

if %changes% gtr 0 (
    echo ⚠️  You have uncommitted changes.
    set /p commit="Do you want to commit them? (y/n): "
    if /i "%commit%"=="y" (
        git add .
        git commit -m "Deploy to production"
    )
)

REM Push to GitHub
echo ✅ Pushing to GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo ✅ Code pushed to GitHub successfully!
) else (
    echo ❌ Failed to push to GitHub
    pause
    exit /b 1
)

echo.
echo 🎯 Next Steps:
echo ==============
echo.
echo 1. 🎨 Deploy Frontend to Vercel:
echo    - Go to https://vercel.com
echo    - Import your GitHub repository
echo    - Set Root Directory to 'frontend'
echo    - Add environment variable: NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
echo.
echo 2. ⚙️ Deploy Backend to Railway:
echo    - Go to https://railway.app
echo    - Import your GitHub repository
echo    - Add environment variables:
echo      - SUPABASE_URL=your_supabase_url
echo      - SUPABASE_ANON_KEY=your_supabase_anon_key
echo      - SUPABASE_SERVICE_KEY=your_supabase_service_key
echo      - SECRET_KEY=your_jwt_secret_key
echo.
echo 3. 🗄️ Set up Supabase:
echo    - Run the SQL schema from SETUP_GUIDE.md
echo    - Configure RLS policies
echo.
echo 4. 🔗 Connect Frontend to Backend:
echo    - Update NEXT_PUBLIC_API_URL in Vercel with your Railway URL
echo    - Redeploy frontend
echo.
echo 📚 For detailed instructions, see DEPLOYMENT_GUIDE.md
echo.
echo ✅ Deployment preparation complete! 🚀
pause
