# 🚀 Deployment Guide - Vercel + Railway

This guide will help you deploy the Premium Scraper to production using Vercel for the frontend and Railway for the backend.

## 📋 Prerequisites

- GitHub account
- Vercel account (free)
- Railway account (free)
- Supabase project set up
- Domain name (optional)

## 🎨 **Frontend Deployment (Vercel)**

### Step 1: Prepare Frontend for Vercel

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

2. **Verify frontend configuration:**
   - ✅ `frontend/vercel.json` exists
   - ✅ `frontend/.vercelignore` exists
   - ✅ `frontend/next.config.js` is configured
   - ✅ `frontend/package.json` has build scripts

### Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Import your repository**
5. **Configure project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

6. **Set Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
   ```

7. **Deploy!**
   - Click "Deploy"
   - Wait for build to complete
   - Your frontend will be live at `https://your-project.vercel.app`

### Step 3: Configure Custom Domain (Optional)

1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Domains"
   - Add your custom domain
   - Configure DNS settings

## ⚙️ **Backend Deployment (Railway)**

### Step 1: Prepare Backend for Railway

1. **Verify backend configuration:**
   - ✅ `railway.json` exists
   - ✅ `Procfile` exists
   - ✅ `runtime.txt` exists
   - ✅ `requirements-prod.txt` exists

2. **Update environment variables in your code:**
   ```python
   # In src/config/supabase.py
   self.url: str = os.getenv("SUPABASE_URL", "")
   self.key: str = os.getenv("SUPABASE_ANON_KEY", "")
   self.service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
   ```

### Step 2: Deploy to Railway

1. **Go to [railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Configure deployment:**
   - **Root Directory:** `/` (root)
   - **Build Command:** `pip install -r requirements-prod.txt`
   - **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

7. **Set Environment Variables:**
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   SECRET_KEY=your_jwt_secret_key_here
   PORT=8000
   ```

8. **Deploy!**
   - Railway will automatically build and deploy
   - Your backend will be live at `https://your-project.railway.app`

### Step 3: Configure Railway Settings

1. **In Railway Dashboard:**
   - Go to your project
   - Click "Settings"
   - Configure:
     - **Health Check:** `/health`
     - **Restart Policy:** On Failure
     - **Max Retries:** 10

## 🔗 **Connect Frontend to Backend**

### Step 1: Update Frontend Environment

1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Settings" → "Environment Variables"
   - Update `NEXT_PUBLIC_API_URL` to your Railway URL:
     ```
     NEXT_PUBLIC_API_URL=https://your-project.railway.app
     ```

2. **Redeploy frontend:**
   - Go to "Deployments"
   - Click "Redeploy"

### Step 2: Test Connection

1. **Visit your Vercel frontend URL**
2. **Check browser console for errors**
3. **Test API endpoints:**
   - `https://your-railway-backend-url.railway.app/health`
   - `https://your-railway-backend-url.railway.app/docs`

## 🗄️ **Database Setup (Supabase)**

### Step 1: Configure Supabase

1. **Go to your Supabase project**
2. **Run the SQL schema** (from `SETUP_GUIDE.md`)
3. **Configure RLS policies**
4. **Set up authentication** (if using Supabase Auth)

### Step 2: Update Environment Variables

**In Railway (Backend):**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

**In Vercel (Frontend) - Optional:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## 🔧 **Production Configuration**

### Backend Optimizations

1. **Update `src/api/main.py`:**
```python
# Production settings
if os.getenv("ENVIRONMENT") == "production":
    app = FastAPI(
        title="Premium Scraper API",
        description="Production API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        # Disable docs in production if needed
        # docs_url=None,
        # redoc_url=None,
    )
```

2. **Add CORS configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Optimizations

1. **Update `frontend/next.config.js`:**
```javascript
const nextConfig = {
  // ... existing config
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}
```

## 📊 **Monitoring & Logs**

### Railway Monitoring

1. **View logs:**
   - Go to Railway dashboard
   - Click "Deployments"
   - View real-time logs

2. **Monitor metrics:**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Vercel Monitoring

1. **View analytics:**
   - Go to Vercel dashboard
   - Click "Analytics"
   - View performance metrics

2. **View function logs:**
   - Go to "Functions" tab
   - View serverless function logs

## 🚨 **Troubleshooting**

### Common Issues

1. **Frontend can't connect to backend:**
   - Check `NEXT_PUBLIC_API_URL` in Vercel
   - Verify Railway backend is running
   - Check CORS settings

2. **Backend deployment fails:**
   - Check Railway logs
   - Verify `requirements-prod.txt`
   - Check environment variables

3. **Database connection issues:**
   - Verify Supabase credentials
   - Check RLS policies
   - Test database connection

### Debug Steps

1. **Check Railway logs:**
```bash
# In Railway dashboard
# Go to Deployments → View Logs
```

2. **Check Vercel function logs:**
```bash
# In Vercel dashboard
# Go to Functions → View Logs
```

3. **Test API endpoints:**
```bash
curl https://your-railway-backend-url.railway.app/health
curl https://your-railway-backend-url.railway.app/docs
```

## 🔒 **Security Considerations**

### Production Security

1. **Environment Variables:**
   - Never commit secrets to Git
   - Use strong JWT secret keys
   - Rotate keys regularly

2. **CORS Configuration:**
   - Only allow your frontend domains
   - Remove wildcard origins

3. **Rate Limiting:**
   - Implement API rate limiting
   - Use Railway's built-in protection

4. **HTTPS:**
   - Both Vercel and Railway provide HTTPS
   - No additional configuration needed

## 📈 **Scaling Considerations**

### Railway Scaling

1. **Upgrade plan** for more resources
2. **Add multiple instances** for high availability
3. **Use Railway's database** for better performance

### Vercel Scaling

1. **Vercel automatically scales**
2. **Edge functions** for global performance
3. **CDN** for static assets

## 💰 **Cost Optimization**

### Free Tier Limits

**Vercel:**
- 100GB bandwidth/month
- Unlimited static sites
- Serverless functions

**Railway:**
- $5 credit/month
- 512MB RAM
- 1GB storage

### Upgrade When Needed

**Vercel Pro:** $20/month
- Unlimited bandwidth
- Advanced analytics
- Priority support

**Railway Pro:** $5/month
- More resources
- Better performance
- Priority support

## 🎯 **Next Steps**

1. **Set up monitoring** with external services
2. **Configure backups** for Supabase
3. **Add CI/CD** with GitHub Actions
4. **Set up alerts** for downtime
5. **Optimize performance** based on usage

---

**Your Premium Scraper is now live in production! 🚀**

- **Frontend:** `https://your-project.vercel.app`
- **Backend:** `https://your-project.railway.app`
- **API Docs:** `https://your-project.railway.app/docs`
