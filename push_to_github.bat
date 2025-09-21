@echo off
echo 🚀 Pushing Premium Scraper to GitHub...
echo.

echo 📋 Checking git status...
git status --porcelain

echo.
echo 📦 Adding all files...
git add .

echo.
echo 💾 Committing changes...
git commit -m "Add Premium Scraper with Supabase integration and Next.js frontend"

echo.
echo 🚀 Pushing to GitHub...
git push origin master

echo.
echo ✅ Push completed!
echo.
echo 🎯 Next steps:
echo 1. Go to https://railway.app
echo 2. Connect your GitHub repository
echo 3. Deploy your backend
echo.
pause
