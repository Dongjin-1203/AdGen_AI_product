/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', 
  images: {
    domains: ['storage.googleapis.com'],
  },
}

module.exports = nextConfig
