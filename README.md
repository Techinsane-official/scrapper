# 🚀 Premium E-commerce Scraper

A professional, enterprise-grade e-commerce product scraping platform with Supabase integration and a modern Next.js web panel.

## ✨ Features

### 🔧 Backend (FastAPI + Supabase)
- **Multi-retailer Support** - Amazon, Walmart, eBay, and more
- **Advanced Anti-Detection** - Rotating user agents, proxy support, rate limiting
- **Real-time Monitoring** - Live job status, progress tracking, error handling
- **Scalable Architecture** - Async processing, background tasks, queue management
- **Professional API** - RESTful endpoints, authentication, comprehensive documentation
- **Database Integration** - Supabase PostgreSQL with real-time subscriptions
- **Comprehensive Logging** - Structured logging, error tracking, performance metrics

### 🎨 Frontend (Next.js + TypeScript)
- **Modern Dashboard** - Real-time statistics, job management, data visualization
- **Responsive Design** - Mobile-first, works on all devices
- **Authentication System** - JWT-based auth with role management
- **Real-time Updates** - Live job progress, notifications, activity feeds
- **Professional UI** - Tailwind CSS, Headless UI components
- **Type Safety** - Full TypeScript implementation
- **Performance Optimized** - React Query caching, optimized builds

### 📊 Data Management
- **Product Catalog** - Comprehensive product data storage
- **Search & Filter** - Advanced product search capabilities
- **Export Options** - CSV, JSON, Excel export formats
- **Data Validation** - Schema validation, data quality checks
- **Analytics** - Success rates, performance metrics, usage statistics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Premium Scraper Platform                 │
├─────────────────────────────────────────────────────────────┤
│  Next.js Frontend (Port 3000)                              │
│  ├── Dashboard & Analytics                                │
│  ├── Job Management                                        │
│  ├── Product Browser                                      │
│  └── User Management                                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                              │
│  ├── RESTful API                                          │
│  ├── Authentication & Authorization                       │
│  ├── Background Job Processing                             │
│  ├── Rate Limiting & Anti-Detection                       │
│  └── Real-time WebSocket Updates                          │
├─────────────────────────────────────────────────────────────┤
│  Supabase Cloud Database                                  │
│  ├── PostgreSQL Database                                  │
│  ├── Real-time Subscriptions                              │
│  ├── Row Level Security                                   │
│  └── Built-in Authentication                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd Escrapper
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your Supabase credentials

# Start backend server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
copy .env.example .env.local
# Edit .env.local with your API URL

# Start frontend server
npm run dev
```

### 4. Database Setup
1. Create a Supabase project
2. Run the SQL schema from `SETUP_GUIDE.md`
3. Configure environment variables

### 5. Access the Platform
- **Frontend Panel:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🛠️ Development

### Using the Development Scripts

**Windows:**
```bash
# Start both servers
start_dev.bat
```

**Linux/Mac:**
```bash
# Start both servers
python start_dev.py
```

### Manual Development

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn src.api.main:app --reload

# Run tests
pytest

# Format code
black src/
flake8 src/
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

## 📁 Project Structure

```
Escrapper/
├── src/                          # Backend source code
│   ├── api/                      # FastAPI application
│   │   ├── main.py              # Main FastAPI app
│   │   ├── auth.py              # Authentication logic
│   │   └── routes/              # API route handlers
│   ├── config/                   # Configuration
│   │   └── supabase.py          # Supabase client setup
│   ├── database/                 # Database layer
│   │   ├── models.py            # Pydantic models
│   │   └── service.py           # Database operations
│   └── scraper/                  # Scraping modules
│       ├── base.py              # Base scraper class
│       └── amazon.py             # Amazon scraper
├── frontend/                     # Next.js frontend
│   ├── app/                      # Next.js 13+ app directory
│   │   ├── auth/                # Authentication pages
│   │   ├── dashboard/           # Dashboard pages
│   │   └── layout.tsx           # Root layout
│   ├── components/              # React components
│   │   ├── dashboard/           # Dashboard components
│   │   ├── jobs/               # Job management
│   │   └── layout/             # Layout components
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utility libraries
│   └── types/                   # TypeScript definitions
├── logs/                         # Application logs
├── tests/                        # Test files
├── requirements.txt              # Python dependencies
├── start_dev.py                  # Development startup script
├── start_dev.bat                 # Windows startup script
└── SETUP_GUIDE.md               # Detailed setup instructions
```

## 🔐 Authentication & Security

### User Roles
- **Admin** - Full system access, user management
- **User** - Create jobs, view own data
- **Viewer** - Read-only access

### Security Features
- JWT token authentication
- Row Level Security (RLS) in Supabase
- Rate limiting and request throttling
- Input validation and sanitization
- CORS protection
- Secure environment variable handling

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Jobs Management
- `GET /api/jobs` - List user jobs
- `POST /api/jobs` - Create new job
- `GET /api/jobs/{id}` - Get job details
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job

### Products
- `GET /api/products/job/{job_id}` - Get job products
- `GET /api/products/{id}` - Get product details
- `GET /api/products/search` - Search products

### Dashboard
- `GET /api/dashboard` - Dashboard data
- `GET /api/dashboard/stats` - Statistics

## 🎯 Supported Retailers

### Currently Supported
- **Amazon** - Full product data extraction
  - Product details, pricing, reviews
  - Images, specifications, variations
  - Category-based and search-based scraping

### Planned Support
- **Walmart** - Product catalog scraping
- **eBay** - Auction and fixed-price items
- **Target** - Retail product data
- **Best Buy** - Electronics and tech products

## 📈 Monitoring & Analytics

### Real-time Metrics
- Job success/failure rates
- Products scraped per hour
- System performance metrics
- User activity tracking

### Logging
- Structured JSON logging
- Error tracking and alerting
- Performance monitoring
- Audit trails

## 🚀 Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t premium-scraper .
docker run -p 8000:8000 premium-scraper

# Using Gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
# Vercel (Recommended)
npm run build
# Deploy to Vercel

# Other platforms
npm run build
npm run start
```

### Environment Variables
```env
# Backend
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SECRET_KEY=your_jwt_secret_key

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_scraper.py
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed installation instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Frontend README](frontend/README.md)** - Frontend-specific documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- **Database Connection** - Check Supabase credentials
- **Authentication** - Verify JWT secret key
- **Scraping Failures** - Check target website accessibility
- **Build Errors** - Clear cache and reinstall dependencies

### Getting Help
- Check the [Setup Guide](SETUP_GUIDE.md)
- Review API documentation at `/docs`
- Check logs in the `logs/` directory
- Open an issue on GitHub

## 🎯 Roadmap

### Short Term
- [ ] Add more retailers (Walmart, eBay)
- [ ] Implement data export features
- [ ] Add email notifications
- [ ] Create mobile app

### Long Term
- [ ] Machine learning for product matching
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant architecture
- [ ] API rate limiting and quotas

---

**Built with ❤️ for professional e-commerce data extraction**

*For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)*
