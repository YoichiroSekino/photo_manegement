'use client';

import { PhotoGrid } from '@/components/photos/PhotoGrid';
import { usePhotos } from '@/hooks/usePhotos';
import { useUIStore } from '@/store/uiStore';
import { useFilterStore } from '@/store/filterStore';

export default function PhotosPage() {
  // React Queryでデータ取得
  const filters = useFilterStore((state) => state.filters);
  const { data: photos = [], isLoading, error } = usePhotos(filters);

  // UI状態管理
  const { viewMode, setViewMode, sortField, sortOrder, setSorting } =
    useUIStore();

  const handlePhotoSelect = (id: string) => {
    console.log('Selected photo:', id);
    // TODO: 写真詳細ページへ遷移またはモーダル表示
  };

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">写真一覧</h1>
            <p className="text-gray-600">
              アップロードされた工事写真を閲覧・管理できます
            </p>
          </div>

          <div className="flex items-center space-x-4">
            {/* View mode toggle */}
            <div className="flex items-center space-x-2 border rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                aria-label="Grid view"
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
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                aria-label="List view"
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
                    d="M4 6h16M4 12h16M4 18h16"
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
              {photos.length} 件の写真
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

        {!isLoading && !error && (
          <PhotoGrid photos={photos} onPhotoSelect={handlePhotoSelect} />
        )}
      </div>
    </main>
  );
}
