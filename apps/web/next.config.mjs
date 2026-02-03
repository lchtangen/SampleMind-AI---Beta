/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Compiler options
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
    // Remove React StrictMode in production
    styledComponents: true,
  },

  // Image optimization
  images: {
    domains: ['samplemind.ai', 'cdn.samplemind.ai'],
    formats: ['image/avif', 'image/webp'],
    // Add image optimization defaults
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Performance optimizations
  experimental: {
    optimizeCss: true,
    // Enable optimized package imports
    optimizePackageImports: [
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      'framer-motion',
    ],
  },

  // Linting
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Headers with caching strategies
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
      // Cache static assets aggressively
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      // Cache fonts
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },

  // Webpack optimizations
  webpack: (config, { isServer }) => {
    // Optimize client-side bundle
    if (!isServer) {
      // Disable source maps in production
      if (process.env.NODE_ENV === 'production') {
        config.devtool = false
      }

      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }

    // Tree shaking optimization
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: true,
    }

    return config
  },

  // Compression
  compress: true,

  // Optimize production builds
  productionBrowserSourceMaps: false,
}

export default nextConfig
