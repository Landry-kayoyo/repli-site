/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', '127.0.0.1'],
    remotePatterns: [
      { protocol: 'http', hostname: '**' },
      { protocol: 'https', hostname: '**' },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' },
      { source: '/media/:path*', destination: 'http://localhost:8000/media/:path*' },
      { source: '/admin', destination: 'http://localhost:8000/admin/' },
      { source: '/admin/:path*', destination: 'http://localhost:8000/admin/:path*' },
      { source: '/ckeditor/:path*', destination: 'http://localhost:8000/ckeditor/:path*' },
      { source: '/rss/:path*', destination: 'http://localhost:8000/rss/:path*' },
      { source: '/sitemap.xml', destination: 'http://localhost:8000/sitemap.xml' },
    ];
  },
}
module.exports = nextConfig
