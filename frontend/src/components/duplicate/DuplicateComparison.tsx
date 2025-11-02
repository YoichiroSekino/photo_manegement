/**
 * 重複写真比較コンポーネント
 */

'use client';

import Image from 'next/image';
import { usePhoto } from '@/hooks/usePhotos';
import { Photo } from '@/types/photo';

export interface DuplicatePair {
  id: number;
  photo1: Photo;
  photo2: Photo;
  similarityScore: number;
  duplicateType: string;
  status: 'pending' | 'confirmed' | 'rejected';
}

interface DuplicateComparisonProps {
  duplicatePair: DuplicatePair;
  onConfirm: (pairId: number, photoToKeep: 'photo1' | 'photo2') => void;
  onReject: (pairId: number) => void;
}

export function DuplicateComparison({
  duplicatePair,
  onConfirm,
  onReject,
}: DuplicateComparisonProps) {
  const { photo1, photo2, similarityScore, status } = duplicatePair;

  // Fetch full photo details if we only have IDs
  const { data: photo1Details } = usePhoto(Number(photo1.id));
  const { data: photo2Details } = usePhoto(Number(photo2.id));

  // Use fetched details if available, otherwise use provided data
  const fullPhoto1 = photo1Details || photo1;
  const fullPhoto2 = photo2Details || photo2;

  const getSimilarityColor = (score: number) => {
    if (score >= 0.95) return 'text-red-600';
    if (score >= 0.85) return 'text-orange-600';
    if (score >= 0.75) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getSimilarityLabel = (score: number) => {
    if (score >= 0.95) return '完全一致';
    if (score >= 0.85) return '非常に類似';
    if (score >= 0.75) return '類似';
    return '若干類似';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-4">
      {/* ヘッダー */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-2">
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
          <h3 className="text-base sm:text-lg font-semibold">重複候補</h3>
          <span
            className={`text-sm sm:text-base font-semibold ${getSimilarityColor(similarityScore)}`}
          >
            {getSimilarityLabel(similarityScore)} ({Math.round(similarityScore * 100)}%)
          </span>
        </div>
        {status !== 'pending' && (
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              status === 'confirmed'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {status === 'confirmed' ? '重複確定' : '重複でない'}
          </span>
        )}
      </div>

      {/* サイドバイサイド比較 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mb-6">
        {/* Photo 1 */}
        <PhotoComparisonCard
          photo={fullPhoto1}
          label="写真 1"
          onSelect={() => onConfirm(duplicatePair.id, 'photo1')}
          disabled={status !== 'pending'}
        />

        {/* Photo 2 */}
        <PhotoComparisonCard
          photo={fullPhoto2}
          label="写真 2"
          onSelect={() => onConfirm(duplicatePair.id, 'photo2')}
          disabled={status !== 'pending'}
        />
      </div>

      {/* アクションボタン */}
      {status === 'pending' && (
        <div className="flex items-center justify-center space-x-4 pt-4 border-t">
          <button
            onClick={() => onReject(duplicatePair.id)}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            重複ではない
          </button>
          <p className="text-sm text-gray-500">
            または、保持したい写真を選択してください
          </p>
        </div>
      )}
    </div>
  );
}

interface PhotoComparisonCardProps {
  photo: Photo;
  label: string;
  onSelect: () => void;
  disabled: boolean;
}

function PhotoComparisonCard({
  photo,
  label,
  onSelect,
  disabled,
}: PhotoComparisonCardProps) {
  return (
    <div className="border rounded-lg overflow-hidden hover:border-blue-500 transition-colors">
      {/* 画像プレビュー */}
      <div className="aspect-video bg-gray-100 relative">
        {photo.s3Url ? (
          <Image
            src={photo.s3Url}
            alt={photo.fileName}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 50vw"
            priority={false}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <svg
              className="w-16 h-16 text-gray-400"
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
        <div className="absolute top-2 left-2 bg-black bg-opacity-60 text-white px-2 py-1 rounded text-sm font-medium">
          {label}
        </div>
      </div>

      {/* 詳細情報 */}
      <div className="p-4">
        <h4 className="font-medium text-sm truncate mb-2">{photo.fileName}</h4>
        <div className="space-y-1 text-xs text-gray-600">
          <p>
            サイズ: {photo.metadata?.width} × {photo.metadata?.height}
          </p>
          <p>
            容量: {(photo.fileSize / 1024 / 1024).toFixed(2)} MB
          </p>
          {photo.shootingDate && (
            <p>撮影日: {new Date(photo.shootingDate).toLocaleDateString('ja-JP')}</p>
          )}
          {photo.category?.photoType && (
            <p>種別: {photo.category.photoType}</p>
          )}
        </div>

        {/* 保持ボタン */}
        {!disabled && (
          <button
            onClick={onSelect}
            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            この写真を保持
          </button>
        )}
      </div>
    </div>
  );
}
