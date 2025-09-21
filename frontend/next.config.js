/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    // Only use rewrites in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
        },
      ]
    }
    return []
  },
  images: {
    domains: [
      'images-na.ssl-images-amazon.com', 
      'm.media-amazon.com',
      'images-na.ssl-images-amazon.com',
      'images-amazon.com',
      'amazon.com'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.amazon.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**.ssl-images-amazon.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  // Optimize for Vercel
  experimental: {
    optimizeCss: true,
  },
  // Enable compression
  compress: true,
  // Power optimization
  poweredByHeader: false,
}

module.exports = nextConfig
