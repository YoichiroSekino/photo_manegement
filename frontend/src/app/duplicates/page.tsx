/**
 * 重複検出ページ
 */

'use client';

import { useState } from 'react';
import {
  DuplicateComparison,
  DuplicatePair,
} from '@/components/duplicate/DuplicateComparison';

export default function DuplicatesPage() {
  // TODO: 実際のデータはAPIから取得
  const [duplicatePairs, setDuplicatePairs] = useState<DuplicatePair[]>([]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'confirmed' | 'rejected'>('pending');
  const [isLoading, setIsLoading] = useState(false);

  const handleConfirm = async (pairId: number, photoToKeep: 'photo1' | 'photo2') => {
    // TODO: APIに重複確定リクエストを送信
    console.log('Confirm duplicate:', pairId, 'Keep:', photoToKeep);

    setDuplicatePairs((prev) =>
      prev.map((pair) =>
        pair.id === pairId ? { ...pair, status: 'confirmed' as const } : pair
      )
    );
  };

  const handleReject = async (pairId: number) => {
    // TODO: APIに重複却下リクエストを送信
    console.log('Reject duplicate:', pairId);

    setDuplicatePairs((prev) =>
      prev.map((pair) =>
        pair.id === pairId ? { ...pair, status: 'rejected' as const } : pair
      )
    );
  };

  const handleDetectDuplicates = async () => {
    setIsLoading(true);
    try {
      // TODO: 重複検出APIを呼び出す
      const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiEndpoint}/api/v1/photos/detect-duplicates`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Duplicate detection failed');
      }

      const result = await response.json();
      console.log('Duplicate detection result:', result);

      // TODO: 結果を取得してdupplicatePairsに設定
    } catch (error) {
      console.error('Error detecting duplicates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPairs = duplicatePairs.filter((pair) => {
    if (filter === 'all') return true;
    return pair.status === filter;
  });

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-7xl mx-auto w-full">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">重複検出</h1>
          <p className="text-gray-600">
            類似した写真を検出し、重複を確認・削除できます
          </p>
        </div>

        {/* アクションバー */}
        <div className="flex items-center justify-between mb-6">
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
            disabled={isLoading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isLoading ? (
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
