/**
 * 重複検出ページ
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import {
  DuplicateComparison,
  DuplicatePair,
} from '@/components/duplicate/DuplicateComparison';
import { useDetectDuplicates, usePhoto } from '@/hooks/usePhotos';
import { Photo } from '@/types/photo';

interface DuplicateGroup {
  group_id: number;
  photos: Array<{
    id: number;
    file_name: string;
    phash: string;
    similarity?: number;
  }>;
  avg_similarity: number;
  photo_count: number;
}

export default function DuplicatesPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [duplicatePairs, setDuplicatePairs] = useState<DuplicatePair[]>([]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'confirmed' | 'rejected'>('pending');
  const { mutate: detectDuplicates, isPending, data: detectResult } = useDetectDuplicates();

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  // 重複検出結果を処理してペアに変換
  useEffect(() => {
    if (detectResult && detectResult.duplicate_groups) {
      const fetchPhotoDetails = async () => {
        const pairs: DuplicatePair[] = [];
        let pairId = 1;

        // 各グループから全てのペア組み合わせを生成
        for (const group of detectResult.duplicate_groups) {
          const groupPhotos = group.photos;

          // グループ内の写真から全ペアを生成（組み合わせ）
          for (let i = 0; i < groupPhotos.length - 1; i++) {
            for (let j = i + 1; j < groupPhotos.length; j++) {
              // 簡易的な Photo オブジェクトを作成（必要最小限のプロパティ）
              const createPhotoStub = (photoInfo: any): Photo => ({
                id: photoInfo.id.toString(),
                fileName: photoInfo.file_name,
                fileSize: 0,
                mimeType: 'image/jpeg',
                s3Url: '',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
              });

              pairs.push({
                id: pairId++,
                photo1: createPhotoStub(groupPhotos[i]),
                photo2: createPhotoStub(groupPhotos[j]),
                similarityScore: group.avg_similarity / 100, // Convert percentage to 0-1
                duplicateType: 'perceptual',
                status: 'pending',
              });
            }
          }
        }

        setDuplicatePairs(pairs);
      };

      fetchPhotoDetails();
    }
  }, [detectResult]);

  const handleConfirm = async (pairId: number, photoToKeep: 'photo1' | 'photo2') => {
    const pair = duplicatePairs.find((p) => p.id === pairId);
    if (!pair) return;

    const photoIdToKeep = photoToKeep === 'photo1' ? Number(pair.photo1.id) : Number(pair.photo2.id);
    const photoIdToDelete = photoToKeep === 'photo1' ? Number(pair.photo2.id) : Number(pair.photo1.id);

    try {
      // API呼び出し
      const response = await fetch('/api/v1/photos/duplicates/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          photo_id_to_keep: photoIdToKeep,
          photo_id_to_delete: photoIdToDelete,
          action: 'confirm',
        }),
      });

      if (!response.ok) throw new Error('重複確定に失敗しました');

      const result = await response.json();
      console.log('Duplicate confirmed:', result);

      // UI更新
      setDuplicatePairs((prev) =>
        prev.map((p) =>
          p.id === pairId ? { ...p, status: 'confirmed' as const } : p
        )
      );
    } catch (error) {
      console.error('Error confirming duplicate:', error);
      alert('重複確定に失敗しました');
    }
  };

  const handleReject = async (pairId: number) => {
    const pair = duplicatePairs.find((p) => p.id === pairId);
    if (!pair) return;

    try {
      // API呼び出し
      const response = await fetch('/api/v1/photos/duplicates/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          photo_id_to_keep: Number(pair.photo1.id),
          photo_id_to_delete: Number(pair.photo2.id),
          action: 'reject',
        }),
      });

      if (!response.ok) throw new Error('重複却下に失敗しました');

      const result = await response.json();
      console.log('Duplicate rejected:', result);

      // UI更新
      setDuplicatePairs((prev) =>
        prev.map((p) =>
          p.id === pairId ? { ...p, status: 'rejected' as const } : p
        )
      );
    } catch (error) {
      console.error('Error rejecting duplicate:', error);
      alert('重複却下に失敗しました');
    }
  };

  const handleDetectDuplicates = () => {
    detectDuplicates({
      similarity_threshold: 90.0,
    });
  };

  const filteredPairs = duplicatePairs.filter((pair) => {
    if (filter === 'all') return true;
    return pair.status === filter;
  });

  return (
    <main className="flex min-h-screen flex-col p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto w-full">
        {/* ヘッダー */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold mb-2">重複検出</h1>
          <p className="text-sm sm:text-base text-gray-600">
            類似した写真を検出し、重複を確認・削除できます
          </p>
        </div>

        {/* アクションバー */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center space-x-4">
            {/* フィルター */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as typeof filter)}
              className="border border-gray-300 rounded-lg px-4 py-2 text-sm"
            >
              <option value="all">すべて</option>
              <option value="pending">未確認</option>
              <option value="confirmed">確定済み</option>
              <option value="rejected">却下済み</option>
            </select>

            <span className="text-sm text-gray-600">
              {filteredPairs.length}件の候補
            </span>
          </div>

          {/* 重複検出ボタン */}
          <button
            onClick={handleDetectDuplicates}
            disabled={isPending}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isPending ? (
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
                <span>検出中...</span>
              </span>
            ) : (
              '重複を検出'
            )}
          </button>
        </div>

        {/* 重複候補リスト */}
        {filteredPairs.length > 0 ? (
          <div className="space-y-4">
            {filteredPairs.map((pair) => (
              <DuplicateComparison
                key={pair.id}
                duplicatePair={pair}
                onConfirm={handleConfirm}
                onReject={handleReject}
              />
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              重複候補がありません
            </h3>
            <p className="text-gray-500">
              「重複を検出」ボタンをクリックして、類似写真を検出してください
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
