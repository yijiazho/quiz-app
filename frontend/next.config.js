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
}

module.exports = nextConfig 