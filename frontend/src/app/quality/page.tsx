/**
 * 品質評価ページ
 */

'use client';

import { useState } from 'react';
import { QualityBadge } from '@/components/quality/QualityBadge';
import { QualityDetails } from '@/components/quality/QualityDetails';
import { Photo } from '@/types/photo';

interface QualityPhoto extends Photo {
  qualityScore: number;
  qualityIssues?: Array<{
    type: string;
    severity: 'high' | 'medium' | 'low';
    message: string;
    recommendation?: string;
  }>;
}

export default function QualityPage() {
  // TODO: 実際のデータはAPIから取得
  const [photos, setPhotos] = useState<QualityPhoto[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<QualityPhoto | null>(null);
  const [qualityFilter, setQualityFilter] = useState<'all' | 'good' | 'fair' | 'poor'>('all');
  const [isAssessing, setIsAssessing] = useState(false);

  const handleAssessQuality = async () => {
    setIsAssessing(true);
    try {
      // TODO: 品質評価APIを呼び出す
      const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiEndpoint}/api/v1/photos/assess-quality`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Quality assessment failed');
      }

      const result = await response.json();
      console.log('Quality assessment result:', result);

      // TODO: 結果を取得してphotosに設定
    } catch (error) {
      console.error('Error assessing quality:', error);
    } finally {
      setIsAssessing(false);
    }
  };

  const getFilteredPhotos = () => {
    if (qualityFilter === 'all') return photos;
    if (qualityFilter === 'good') return photos.filter((p) => p.qualityScore >= 80);
    if (qualityFilter === 'fair')
      return photos.filter((p) => p.qualityScore >= 40 && p.qualityScore < 80);
    if (qualityFilter === 'poor') return photos.filter((p) => p.qualityScore < 40);
    return photos;
  };

  const filteredPhotos = getFilteredPhotos();

  // 品質統計
  const stats = {
    total: photos.length,
    good: photos.filter((p) => p.qualityScore >= 80).length,
    fair: photos.filter((p) => p.qualityScore >= 40 && p.qualityScore < 80).length,
    poor: photos.filter((p) => p.qualityScore < 40).length,
    average:
      photos.length > 0
        ? Math.round(
            photos.reduce((sum, p) => sum + p.qualityScore, 0) / photos.length
          )
        : 0,
  };

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-7xl mx-auto w-full">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">品質評価</h1>
          <p className="text-gray-600">
            写真の品質を評価し、基準を満たさない写真を特定します
          </p>
        </div>

        {/* 統計カード */}
        {photos.length > 0 && (
          <div className="grid grid-cols-5 gap-4 mb-6">
            <StatCard label="総写真数" value={stats.total} />
            <StatCard label="平均スコア" value={`${stats.average}点`} color="text-blue-600" />
            <StatCard label="優良" value={stats.good} color="text-green-600" />
            <StatCard label="標準" value={stats.fair} color="text-yellow-600" />
            <StatCard label="要改善" value={stats.poor} color="text-red-600" />
          </div>
        )}

        {/* アクションバー */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            {/* 品質フィルター */}
            <select
              value={qualityFilter}
              onChange={(e) => setQualityFilter(e.target.value as typeof qualityFilter)}
              className="border border-gray-300 rounded-lg px-4 py-2 text-sm"
            >
              <option value="all">すべて</option>
              <option value="good">優良（80点以上）</option>
              <option value="fair">標準（40-79点）</option>
              <option value="poor">要改善（40点未満）</option>
            </select>

            <span className="text-sm text-gray-600">
              {filteredPhotos.length}件の写真
            </span>
          </div>

          {/* 品質評価ボタン */}
          <button
            onClick={handleAssessQuality}
            disabled={isAssessing}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isAssessing ? (
              <span className="flex items-center space-x-2">
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>評価中...</span>
              </span>
            ) : (
              '品質を評価'
            )}
          </button>
        </div>

        {/* 写真グリッド */}
        {filteredPhotos.length > 0 ? (
          <div className="grid grid-cols-4 gap-6">
            {filteredPhotos.map((photo) => (
              <div
                key={photo.id}
                onClick={() => setSelectedPhoto(photo)}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
              >
                <div className="aspect-video bg-gray-100 relative">
                  {photo.s3Url ? (
                    <img
                      src={photo.s3Url}
                      alt={photo.fileName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <svg
                        className="w-12 h-12 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    <QualityBadge score={photo.qualityScore} showLabel={false} />
                  </div>
                </div>
                <div className="p-3">
                  <p className="text-sm font-medium truncate">{photo.fileName}</p>
                  <div className="mt-2">
                    <QualityBadge score={photo.qualityScore} size="sm" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              品質評価データがありません
            </h3>
            <p className="text-gray-500">
              「品質を評価」ボタンをクリックして、写真の品質を評価してください
            </p>
          </div>
        )}

        {/* 詳細モーダル */}
        {selectedPhoto && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8"
            onClick={() => setSelectedPhoto(null)}
          >
            <div
              className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">{selectedPhoto.fileName}</h2>
                  <button
                    onClick={() => setSelectedPhoto(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <img
                      src={selectedPhoto.s3Url}
                      alt={selectedPhoto.fileName}
                      className="w-full rounded-lg"
                    />
                  </div>
                  <div>
                    <QualityDetails
                      score={selectedPhoto.qualityScore}
                      sharpness={selectedPhoto.metadata?.quality?.sharpness}
                      brightness={selectedPhoto.metadata?.quality?.brightness}
                      contrast={selectedPhoto.metadata?.quality?.contrast}
                      issues={selectedPhoto.qualityIssues}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

interface StatCardProps {
  label: string;
  value: number | string;
  color?: string;
}

function StatCard({ label, value, color = 'text-gray-900' }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
