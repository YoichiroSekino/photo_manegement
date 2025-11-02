'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { SearchBar } from '@/components/search/SearchBar';
import { FilterPanel, FilterOptions } from '@/components/search/FilterPanel';
import { PhotoGrid } from '@/components/photos/PhotoGrid';
import { PhotoDetailModal } from '@/components/photos/PhotoDetailModal';
import { useSearchPhotos, usePhoto } from '@/hooks/usePhotos';
import { useFilterStore } from '@/store/filterStore';

export default function SearchPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const { mutate: searchPhotos, data: searchResult, isPending, error } = useSearchPhotos();

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  const filters = useFilterStore((state) => state.filters);
  const setFilter = useFilterStore((state) => state.setFilter);
  const setFilters = useFilterStore((state) => state.setFilters);

  // 選択された写真の詳細を取得
  const { data: selectedPhoto } = usePhoto(selectedPhotoId);

  const performSearch = useCallback(() => {
    searchPhotos({
      searchQuery: filters.searchQuery,
      workType: filters.workType,
      majorCategory: filters.majorCategory,
      photoType: filters.photoType,
      startDate: filters.startDate,
      endDate: filters.endDate,
      location: filters.location,
      photographer: filters.photographer,
    });
  }, [filters, searchPhotos]);

  const handlePhotoSelect = (id: string) => {
    setSelectedPhotoId(Number(id));
  };

  const handleCloseModal = () => {
    setSelectedPhotoId(null);
  };

  const handleSearch = useCallback((searchKeyword: string) => {
    setFilter('searchQuery', searchKeyword);
  }, [setFilter]);

  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    setFilters({
      ...filters,
      workType: newFilters.workType,
      majorCategory: newFilters.majorCategory,
      photoType: newFilters.photoType,
      startDate: newFilters.dateFrom,
      endDate: newFilters.dateTo,
    });
  }, [filters, setFilters]);

  // フィルター変更時に自動検索
  useEffect(() => {
    performSearch();
  }, [performSearch]);

  return (
    <main className="flex min-h-screen flex-col p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto w-full">
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">写真検索</h1>
        <p className="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8">
          キーワードやフィルターを使用して写真を検索できます。
        </p>

        <div className="space-y-3 sm:space-y-4 mb-6 sm:mb-8">
          <SearchBar onSearch={handleSearch} />
          <FilterPanel onFilterChange={handleFilterChange} />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">検索中にエラーが発生しました</p>
          </div>
        )}

        {isPending ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {searchResult?.length || 0}件の写真が見つかりました
              </p>
            </div>

            {searchResult && searchResult.length > 0 ? (
              <PhotoGrid photos={searchResult} onPhotoSelect={handlePhotoSelect} />
            ) : (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">写真が見つかりませんでした</h3>
                <p className="mt-1 text-sm text-gray-500">
                  別のキーワードやフィルターで試してみてください。
                </p>
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
