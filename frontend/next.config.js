/** @type {import('next').NextConfig} */
const nextConfig = {
  // 画像最適化設定
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.amazonaws.com',
      },
      // 開発環境用：ローカルバックエンド
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/static/uploads/**',
      },
    ],
    formats: ['image/webp', 'image/avif'],
    // 画像キャッシュ最適化
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30日
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // 環境変数
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Strict Mode有効化
  reactStrictMode: true,

  // 出力設定
  output: 'standalone',

  // パフォーマンス最適化
  compiler: {
    // プロダクションビルドでconsole.logを削除
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },
};

module.exports = nextConfig;
