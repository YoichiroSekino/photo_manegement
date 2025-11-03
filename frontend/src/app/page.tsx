'use client';

import { useAuth } from '@/contexts/AuthContext';
import Dashboard from '@/components/Dashboard/Dashboard';
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout';
import Link from 'next/link';

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  // Logged in: Show Dashboard with Layout
  if (user) {
    return (
      <AuthenticatedLayout>
        <Dashboard />
      </AuthenticatedLayout>
    );
  }

  // Not logged in: Show Landing Page
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-6">
          工事写真自動整理システム
        </h1>

        <p className="text-center text-gray-600 mb-8">
          建設現場で撮影される大量の工事写真をAIで自動的に整理・分類し、
          <br />
          国土交通省の「デジタル写真管理情報基準」に準拠した形で管理するシステムです。
        </p>

        <div className="text-center mb-12">
          <Link
            href="/login"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold transition-colors"
          >
            ログインして始める
          </Link>
        </div>

        <div className="grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 lg:text-left gap-4">
          <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
            <h2 className="mb-3 text-2xl font-semibold">
              AI自動分類{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                →
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm opacity-50">
              画像認識とOCRによる自動整理
            </p>
          </div>

          <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
            <h2 className="mb-3 text-2xl font-semibold">
              位置情報管理{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                →
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm opacity-50">
              GPS情報による地図表示と検索
            </p>
          </div>

          <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
            <h2 className="mb-3 text-2xl font-semibold">
              電子納品対応{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                →
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm opacity-50">
              PHOTO.XML自動生成
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
