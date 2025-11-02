'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { PhotoGrid } from '@/components/photos/PhotoGrid';
import { PhotoDetailModal } from '@/components/photos/PhotoDetailModal';
import { PhotoMap } from '@/components/map/PhotoMap';
import { usePhotos, usePhoto } from '@/hooks/usePhotos';
import { useUIStore } from '@/store/uiStore';
import { useFilterStore } from '@/store/filterStore';

export default function PhotosPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const [displayMode, setDisplayMode] = useState<'grid' | 'map'>('grid');
  const pageSize = 20;

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  // React Queryでデータ取得
  const filters = useFilterStore((state) => state.filters);
  const { data, isLoading, error } = usePhotos({ ...filters, page: currentPage, page_size: pageSize });
  const photos = data?.photos || [];
  const totalPages = data?.total_pages || 0;
  const totalCount = data?.total || 0;

  // 選択された写真の詳細を取得
  const { data: selectedPhoto } = usePhoto(selectedPhotoId);

  // UI状態管理
  const { viewMode, setViewMode, sortField, sortOrder, setSorting } =
    useUIStore();

  const handlePhotoSelect = (id: string) => {
    setSelectedPhotoId(Number(id));
  };

  const handleCloseModal = () => {
    setSelectedPhotoId(null);
  };

  return (
    <main className="flex min-h-screen flex-col p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">写真一覧</h1>
            <p className="text-sm sm:text-base text-gray-600">
              アップロードされた工事写真を閲覧・管理できます
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:gap-4">
            {/* Display mode toggle */}
            <div className="flex items-center space-x-2 border rounded-lg p-1">
              <button
                onClick={() => setDisplayMode('grid')}
                className={`p-2 rounded ${displayMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                aria-label="Grid view"
                title="グリッド表示"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
              </button>
              <button
                onClick={() => setDisplayMode('map')}
                className={`p-2 rounded ${displayMode === 'map' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                aria-label="Map view"
                title="地図表示"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                  />
                </svg>
              </button>
            </div>

            {/* Sort dropdown */}
            <select
              value={`${sortField}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-') as [
                  typeof sortField,
                  typeof sortOrder,
                ];
                setSorting(field, order);
              }}
              className="border rounded-lg px-3 py-2 text-sm"
            >
              <option value="date-desc">新しい順</option>
              <option value="date-asc">古い順</option>
              <option value="name-asc">名前順 (A-Z)</option>
              <option value="name-desc">名前順 (Z-A)</option>
            </select>

            <span className="text-sm text-gray-500">
              {totalCount} 件の写真
            </span>
          </div>
        </div>

        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">読み込み中...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-12">
            <p className="text-red-600">写真の読み込みに失敗しました</p>
          </div>
        )}

        {!isLoading && !error && photos.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="mt-4 text-gray-600">写真がアップロードされていません</p>
            <button
              onClick={() => router.push('/upload')}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              写真をアップロードする →
            </button>
          </div>
        )}

        {!isLoading && !error && photos.length > 0 && (
          <>
            {/* Display based on mode */}
            {displayMode === 'grid' ? (
              <PhotoGrid photos={photos} onPhotoSelect={handlePhotoSelect} />
            ) : (
              <PhotoMap photos={photos} onPhotoSelect={handlePhotoSelect} />
            )}

            {/* Pagination - only for grid view */}
            {displayMode === 'grid' && totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center space-x-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  前へ
                </button>

                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 7) {
                      pageNum = i + 1;
                    } else if (currentPage <= 4) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 3) {
                      pageNum = totalPages - 6 + i;
                    } else {
                      pageNum = currentPage - 3 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-3 py-1 rounded ${currentPage === pageNum ? 'bg-blue-600 text-white' : 'hover:bg-gray-100'}`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  次へ
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Photo Detail Modal */}
      {selectedPhoto && (
        <PhotoDetailModal
          photo={selectedPhoto}
          onClose={handleCloseModal}
        />
      )}
    </main>
  );
}
