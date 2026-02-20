/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // ⭐ ESLint 빌드 시 무시 (빠른 배포용)
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // ⭐ TypeScript 에러도 무시 (필요시)
  typescript: {
    ignoreBuildErrors: true,
  },
  
  reactStrictMode: true,
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  images: {
    domains: ['storage.googleapis.com', 'localhost'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
}

module.exports = nextConfig