import type { NextConfig } from 'next';

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://tunetutor.onrender.com/api/:path*', // Proxy to external API
      },
    ];
  },
};

export default nextConfig;