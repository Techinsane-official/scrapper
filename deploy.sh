#!/bin/bash

echo "🚀 Premium Scraper Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not initialized. Please run 'git init' first."
    exit 1
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "You're not on the main branch. Current branch: $current_branch"
    read -p "Do you want to continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes."
    read -p "Do you want to commit them? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Deploy to production"
    fi
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    print_error "No remote origin found. Please add a GitHub remote:"
    echo "git remote add origin https://github.com/yourusername/yourrepo.git"
    exit 1
fi

# Push to GitHub
print_status "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    print_status "Code pushed to GitHub successfully!"
else
    print_error "Failed to push to GitHub"
    exit 1
fi

echo
echo "🎯 Next Steps:"
echo "=============="
echo
echo "1. 🎨 Deploy Frontend to Vercel:"
echo "   - Go to https://vercel.com"
echo "   - Import your GitHub repository"
echo "   - Set Root Directory to 'frontend'"
echo "   - Add environment variable: NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app"
echo
echo "2. ⚙️ Deploy Backend to Railway:"
echo "   - Go to https://railway.app"
echo "   - Import your GitHub repository"
echo "   - Add environment variables:"
echo "     - SUPABASE_URL=your_supabase_url"
echo "     - SUPABASE_ANON_KEY=your_supabase_anon_key"
echo "     - SUPABASE_SERVICE_KEY=your_supabase_service_key"
echo "     - SECRET_KEY=your_jwt_secret_key"
echo
echo "3. 🗄️ Set up Supabase:"
echo "   - Run the SQL schema from SETUP_GUIDE.md"
echo "   - Configure RLS policies"
echo
echo "4. 🔗 Connect Frontend to Backend:"
echo "   - Update NEXT_PUBLIC_API_URL in Vercel with your Railway URL"
echo "   - Redeploy frontend"
echo
echo "📚 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo
print_status "Deployment preparation complete! 🚀"
