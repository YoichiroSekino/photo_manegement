/**
 * 品質評価ページ
 */

'use client';

import { useState, useMemo } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { QualityBadge } from '@/components/quality/QualityBadge';
import { QualityDetails } from '@/components/quality/QualityDetails';
import { usePhotos, useAssessQuality } from '@/hooks/usePhotos';
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
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [selectedPhoto, setSelectedPhoto] = useState<QualityPhoto | null>(null);
  const [qualityFilter, setQualityFilter] = useState<'all' | 'good' | 'fair' | 'poor'>('all');
  const [processingPhotoId, setProcessingPhotoId] = useState<number | null>(null);

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  // 全写真取得
  const { data: photosData } = usePhotos({ page_size: 100 });
  const { mutate: assessQuality } = useAssessQuality();

  // 品質スコアを持つ写真のみ抽出
  const qualityPhotos: QualityPhoto[] = useMemo(() => {
    if (!photosData?.photos) return [];

    return photosData.photos
      .filter(photo => photo.metadata?.quality?.sharpness !== undefined)
      .map(photo => {
        const quality = photo.metadata?.quality;
        const issues = quality?.issues || [];
        const recommendations = quality?.recommendations || [];

        // issuesとrecommendationsを構造化
        const qualityIssues = issues.map((issue, index) => ({
          type: 'quality_check',
          severity: (issue.includes('低') || issue.includes('暗') || issue.includes('不足'))
            ? 'high' as const
            : 'medium' as const,
          message: issue,
          recommendation: recommendations[index] || undefined,
        }));

        return {
          ...photo,
          qualityScore: quality?.score ?? Math.round((quality?.sharpness ?? 0) * 100),
          qualityIssues,
        };
      });
  }, [photosData]);

  const handleAssessQuality = async (photoId: number) => {
    setProcessingPhotoId(photoId);
    try {
      await assessQuality(photoId);
    } finally {
      setProcessingPhotoId(null);
    }
  };

  const getFilteredPhotos = () => {
    if (qualityFilter === 'all') return qualityPhotos;
    if (qualityFilter === 'good') return qualityPhotos.filter((p) => p.qualityScore >= 80);
    if (qualityFilter === 'fair')
      return qualityPhotos.filter((p) => p.qualityScore >= 40 && p.qualityScore < 80);
    if (qualityFilter === 'poor') return qualityPhotos.filter((p) => p.qualityScore < 40);
    return qualityPhotos;
  };

  const filteredPhotos = getFilteredPhotos();

  // 品質統計
  const stats = {
    total: qualityPhotos.length,
    good: qualityPhotos.filter((p) => p.qualityScore >= 80).length,
    fair: qualityPhotos.filter((p) => p.qualityScore >= 40 && p.qualityScore < 80).length,
    poor: qualityPhotos.filter((p) => p.qualityScore < 40).length,
    average:
      qualityPhotos.length > 0
        ? Math.round(
            qualityPhotos.reduce((sum, p) => sum + p.qualityScore, 0) / qualityPhotos.length
          )
        : 0,
  };

  return (
    <main className="flex min-h-screen flex-col p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto w-full">
        {/* ヘッダー */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold mb-2">品質評価</h1>
          <p className="text-sm sm:text-base text-gray-600">
            写真の品質を評価し、基準を満たさない写真を特定します
          </p>
        </div>

        {/* 統計カード */}
        {qualityPhotos.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
            <StatCard label="総写真数" value={stats.total} />
            <StatCard label="平均スコア" value={`${stats.average}点`} color="text-blue-600" />
            <StatCard label="優良" value={stats.good} color="text-green-600" />
            <StatCard label="標準" value={stats.fair} color="text-yellow-600" />
            <StatCard label="要改善" value={stats.poor} color="text-red-600" />
          </div>
        )}

        {/* 未評価写真の情報 */}
        {photosData?.photos && photosData.photos.length > qualityPhotos.length && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-yellow-800">
                {photosData.photos.length - qualityPhotos.length}件の写真が未評価です。写真を選択して個別に品質評価を実行してください。
              </p>
            </div>
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
              {filteredPhotos.length}件の写真（評価済み）
            </span>
          </div>
        </div>

        {/* 写真グリッド */}
        {filteredPhotos.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {filteredPhotos.map((photo) => (
              <div
                key={photo.id}
                onClick={() => setSelectedPhoto(photo)}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
              >
                <div className="aspect-video bg-gray-100 relative">
                  {photo.s3Url ? (
                    <Image
                      src={photo.s3Url}
                      alt={photo.fileName}
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 50vw, 25vw"
                      priority={false}
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
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4 lg:p-8"
            onClick={() => setSelectedPhoto(null)}
          >
            <div
              className="bg-white rounded-lg max-w-4xl w-full max-h-[95vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg sm:text-xl font-bold truncate pr-4">{selectedPhoto.fileName}</h2>
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

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                  <div className="relative aspect-video">
                    {selectedPhoto.s3Url && (
                      <Image
                        src={selectedPhoto.s3Url}
                        alt={selectedPhoto.fileName}
                        fill
                        className="object-contain rounded-lg"
                        sizes="50vw"
                        priority
                      />
                    )}
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
