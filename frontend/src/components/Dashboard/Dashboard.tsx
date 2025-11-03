'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/apiClient';
import StatCard from './StatCard';
import RecentPhotos from './RecentPhotos';
import Link from 'next/link';

interface DashboardStats {
  total_photos: number;
  today_uploads: number;
  this_week_uploads: number;
  duplicates_count: number;
  quality_issues_count: number;
  category_distribution: Record<string, number>;
}

interface Photo {
  id: number;
  file_name: string;
  s3_key: string;
  title: string | null;
  major_category: string | null;
  shooting_date: string | null;
  quality_score: number | null;
  created_at: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentPhotos, setRecentPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [statsData, photosData] = await Promise.all([
          apiClient.get<DashboardStats>('/api/v1/dashboard/stats'),
          apiClient.get<Photo[]>('/api/v1/dashboard/recent-photos?limit=6'),
        ]);
        setStats(statsData);
        setRecentPhotos(photosData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('ダッシュボードデータの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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

  if (error || !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600">{error || 'データの取得に失敗しました'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="text-gray-600 mt-2">工事写真管理システムの概要</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="総写真数"
          value={stats.total_photos.toLocaleString()}
          description="登録されている写真の合計"
        />
        <StatCard
          title="今日のアップロード"
          value={stats.today_uploads.toLocaleString()}
          description="本日アップロードされた写真"
        />
        <StatCard
          title="今週のアップロード"
          value={stats.this_week_uploads.toLocaleString()}
          description="今週アップロードされた写真"
        />
        <StatCard
          title="重複グループ"
          value={stats.duplicates_count.toLocaleString()}
          description="検出された重複写真のグループ数"
        />
      </div>

      {/* Alerts */}
      {stats.quality_issues_count > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>{stats.quality_issues_count}</strong>
                枚の写真に品質の問題があります。
                <Link href="/quality" className="font-medium underline ml-2">
                  確認する →
                </Link>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Category Distribution */}
      {Object.keys(stats.category_distribution).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">カテゴリ別写真数</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(stats.category_distribution).map(([category, count]) => (
              <div key={category} className="border rounded-lg p-4">
                <p className="text-sm text-gray-600">{category}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {count.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Photos */}
      <RecentPhotos photos={recentPhotos} />

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/upload"
          className="bg-blue-600 text-white rounded-lg p-6 text-center hover:bg-blue-700 transition-colors"
        >
          <svg
            className="w-12 h-12 mx-auto mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <span className="text-lg font-semibold">写真をアップロード</span>
        </Link>

        <Link
          href="/search"
          className="bg-green-600 text-white rounded-lg p-6 text-center hover:bg-green-700 transition-colors"
        >
          <svg
            className="w-12 h-12 mx-auto mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <span className="text-lg font-semibold">写真を検索</span>
        </Link>

        <Link
          href="/export"
          className="bg-purple-600 text-white rounded-lg p-6 text-center hover:bg-purple-700 transition-colors"
        >
          <svg
            className="w-12 h-12 mx-auto mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <span className="text-lg font-semibold">エクスポート</span>
        </Link>
      </div>
    </div>
  );
}
