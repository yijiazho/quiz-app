/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Enable production source maps only
  productionBrowserSourceMaps: false,
  // Optimize images
  images: {
    unoptimized: true,
  },
  // Enable webpack optimizations
  webpack: (config, { dev, isServer }) => {
    // Optimize only in production
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        minimize: true,
      }
    }
    return config
  },
  // Add API proxy configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig 