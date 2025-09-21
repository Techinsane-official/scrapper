# Premium Scraper Panel

A professional Next.js web panel for the Premium E-commerce Scraper API.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 🔐 Authentication system with JWT tokens
- 📊 Real-time dashboard with statistics
- 🚀 Job management and monitoring
- 📱 Mobile-friendly design
- ⚡ Fast performance with React Query
- 🎯 TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running Premium Scraper API backend

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env.local
```

3. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js 13+ app directory
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Dashboard pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── components/            # React components
│   ├── dashboard/        # Dashboard components
│   ├── jobs/            # Job-related components
│   └── layout/          # Layout components
├── hooks/               # Custom React hooks
├── lib/                # Utility libraries
│   ├── api.ts          # API client
│   └── auth.ts         # Authentication utilities
└── types/              # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Headless UI** - Accessible UI components
- **Heroicons** - Icon library
- **React Hot Toast** - Toast notifications

## API Integration

The frontend communicates with the Premium Scraper API backend through:

- RESTful API endpoints
- JWT token authentication
- Real-time data updates
- Error handling and user feedback

## Authentication

The app uses JWT-based authentication:

1. User logs in with email/password
2. Backend returns JWT token
3. Token stored in HTTP-only cookies
4. Token included in API requests
5. Automatic token refresh and logout on expiry

## Dashboard Features

- **Statistics Cards** - Overview of jobs, products, and success rates
- **Recent Jobs** - List of latest scraping jobs with status
- **Real-time Updates** - Auto-refresh every 30 seconds
- **Job Creation** - Modal for creating new scraping jobs
- **Notifications** - System notifications and alerts
- **Activity Logs** - Recent system logs and events

## Responsive Design

The panel is fully responsive and works on:

- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## Development

### Adding New Pages

1. Create page component in `app/` directory
2. Add route in navigation if needed
3. Update types in `lib/api.ts` if using new API endpoints

### Adding New Components

1. Create component in appropriate `components/` subdirectory
2. Export from component file
3. Import and use in pages/components

### API Integration

1. Add new API methods to `lib/api.ts`
2. Define TypeScript interfaces for data
3. Use React Query for data fetching
4. Handle loading states and errors

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy automatically

### Other Platforms

1. Build the project: `npm run build`
2. Deploy the `out/` directory
3. Configure environment variables
4. Set up reverse proxy if needed

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL (if using Supabase auth) | No |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | No |

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests if applicable
5. Submit pull request

## License

MIT License - see LICENSE file for details.
