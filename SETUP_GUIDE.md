# Premium Scraper Setup Guide

This guide will help you set up the complete Premium E-commerce Scraper with Supabase integration and Next.js web panel.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Supabase      │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Cloud)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account
- Git

## 🚀 Quick Start

### 1. Clone and Setup Backend

```bash
# Navigate to your project directory
cd Escrapper

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### 2. Configure Supabase

1. **Create Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note down your project URL and API keys

2. **Set Environment Variables:**
   ```bash
   # In your .env file
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   SECRET_KEY=your_jwt_secret_key_here
   ```

3. **Create Database Tables:**
   Run the SQL script below in your Supabase SQL editor:

```sql
-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Scraping jobs table
CREATE TABLE scraping_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    retailer VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    search_query VARCHAR(500),
    max_pages INTEGER DEFAULT 5 CHECK (max_pages > 0 AND max_pages <= 50),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    products_scraped INTEGER DEFAULT 0,
    products_found INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    retailer VARCHAR(100) NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    discount_percentage DECIMAL(5,2),
    rating DECIMAL(3,2),
    review_count INTEGER,
    availability VARCHAR(50) DEFAULT 'unknown',
    brand VARCHAR(255),
    category VARCHAR(255),
    description TEXT,
    bullet_points JSONB DEFAULT '[]',
    specifications JSONB DEFAULT '{}',
    variations JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scraping statistics table
CREATE TABLE scraping_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    products_scraped INTEGER DEFAULT 0,
    products_failed INTEGER DEFAULT 0,
    average_response_time DECIMAL(10,3) DEFAULT 0,
    total_duration DECIMAL(10,3) DEFAULT 0,
    memory_usage DECIMAL(10,2) DEFAULT 0,
    cpu_usage DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System logs table
CREATE TABLE system_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR')),
    message TEXT NOT NULL,
    component VARCHAR(100) NOT NULL,
    job_id UUID REFERENCES scraping_jobs(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications table
CREATE TABLE notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    is_read BOOLEAN DEFAULT false,
    job_id UUID REFERENCES scraping_jobs(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_scraping_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_products_job_id ON products(job_id);
CREATE INDEX idx_products_retailer ON products(retailer);
CREATE INDEX idx_products_external_id ON products(external_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic - you may want to customize these)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own jobs" ON scraping_jobs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own jobs" ON scraping_jobs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own jobs" ON scraping_jobs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own jobs" ON scraping_jobs FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view products from own jobs" ON products FOR SELECT USING (
    EXISTS (SELECT 1 FROM scraping_jobs WHERE scraping_jobs.id = products.job_id AND scraping_jobs.user_id = auth.uid())
);

CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
```

### 3. Start Backend Server

```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
```

Update `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Start Frontend Server

```bash
# Start Next.js development server
npm run dev
```

## 🌐 Access Points

- **Frontend Panel:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

## 🔐 Authentication

### Default Admin User

Create an admin user by running this SQL in Supabase:

```sql
INSERT INTO users (email, full_name, role, is_active) 
VALUES ('admin@example.com', 'Admin User', 'admin', true);
```

### User Registration

1. Go to http://localhost:3000/auth/register
2. Create a new account
3. Sign in at http://localhost:3000/auth/login

## 📊 Dashboard Features

### Main Dashboard
- **Statistics Overview** - Total jobs, active jobs, success rate
- **Recent Jobs** - Latest scraping jobs with real-time status
- **Notifications** - System alerts and job updates
- **Activity Logs** - Recent system events

### Job Management
- **Create Jobs** - Set up new scraping tasks
- **Monitor Progress** - Real-time job status updates
- **View Results** - Browse scraped products
- **Export Data** - Download product data

### Product Browser
- **Search Products** - Find products across all jobs
- **Filter by Retailer** - Amazon, Walmart, etc.
- **View Details** - Complete product information
- **Image Gallery** - Product photos

## 🛠️ Development

### Backend Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black src/
flake8 src/

# Type checking
mypy src/
```

### Frontend Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Type checking
npm run type-check
```

## 🚀 Production Deployment

### Backend (FastAPI)

1. **Using Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Using Gunicorn:**
```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)

1. **Vercel (Recommended):**
   - Connect GitHub repository
   - Set environment variables
   - Deploy automatically

2. **Other Platforms:**
```bash
npm run build
npm run start
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Security
SECRET_KEY=your_jwt_secret_key

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Scraping
MAX_CONCURRENT_REQUESTS=5
REQUEST_DELAY=1.0
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 📈 Monitoring

### Health Checks
- **API Health:** `GET /health`
- **Database Status:** Check Supabase dashboard
- **Frontend Status:** Check browser console

### Logging
- **Backend Logs:** Check `logs/` directory
- **Frontend Logs:** Browser developer tools
- **Supabase Logs:** Supabase dashboard

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Check Supabase URL and keys
   - Verify network connectivity
   - Check RLS policies

2. **Authentication Issues:**
   - Verify JWT secret key
   - Check token expiration
   - Clear browser cookies

3. **Scraping Failures:**
   - Check target website accessibility
   - Verify proxy settings
   - Review rate limiting

4. **Frontend Build Errors:**
   - Clear `.next` directory
   - Reinstall dependencies
   - Check TypeScript errors

### Support

- Check logs in `logs/` directory
- Review Supabase dashboard
- Use browser developer tools
- Check API documentation at `/docs`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🎯 Next Steps

1. **Customize Scrapers** - Add more retailers
2. **Enhance UI** - Add more dashboard widgets
3. **Add Analytics** - Implement data visualization
4. **Scale Infrastructure** - Add load balancing
5. **Add Monitoring** - Implement alerting system

---

**Happy Scraping! 🚀**
