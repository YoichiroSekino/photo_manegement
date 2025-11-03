'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Header() {
  const { user, organization, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo / Title */}
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-gray-900 hover:text-gray-700">
              工事写真管理システム
            </Link>
            {organization && (
              <span className="ml-4 text-sm text-gray-500">
                {organization.name}
              </span>
            )}
          </div>

          {/* Navigation & User Menu */}
          <div className="flex items-center space-x-4">
            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-4">
              <Link
                href="/"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                ダッシュボード
              </Link>
              <Link
                href="/upload"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                アップロード
              </Link>
              <Link
                href="/photos"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                写真一覧
              </Link>
              <Link
                href="/search"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                検索
              </Link>
              <Link
                href="/export"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                エクスポート
              </Link>
            </nav>

            {/* User Info & Logout */}
            <div className="flex items-center space-x-3 border-l border-gray-200 pl-4">
              <div className="text-sm">
                <p className="text-gray-900 font-medium">{user.full_name || user.email}</p>
                <p className="text-gray-500 text-xs">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                ログアウト
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
