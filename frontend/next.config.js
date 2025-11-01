/** @type {import('next').NextConfig} */
const nextConfig = {
  // 画像最適化設定
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.amazonaws.com',
      },
    ],
    formats: ['image/webp', 'image/avif'],
  },

  // 環境変数
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Strict Mode有効化
  reactStrictMode: true,

  // 出力設定
  output: 'standalone',
};

module.exports = nextConfig;
