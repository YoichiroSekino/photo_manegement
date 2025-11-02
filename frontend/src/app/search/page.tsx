'use client';

import { useState, useCallback, useEffect } from 'react';
import { SearchBar } from '@/components/search/SearchBar';
import { FilterPanel, FilterOptions } from '@/components/search/FilterPanel';
import { PhotoGrid } from '@/components/photos/PhotoGrid';
import { Photo } from '@/types/photo';

export default function SearchPage() {
  const [keyword, setKeyword] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalResults, setTotalResults] = useState(0);

  const handleSearch = useCallback(async (searchKeyword: string) => {
    setKeyword(searchKeyword);
    await performSearch(searchKeyword, filters);
  }, [filters]);

  const handleFilterChange = useCallback(async (newFilters: FilterOptions) => {
    setFilters(newFilters);
    await performSearch(keyword, newFilters);
  }, [keyword]);

  const performSearch = async (searchKeyword: string, searchFilters: FilterOptions) => {
    setIsLoading(true);
    setError(null);

    try {
      const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams();

      if (searchKeyword) {
        params.append('keyword', searchKeyword);
      }
      if (searchFilters.workType) {
        params.append('work_type', searchFilters.workType);
      }
      if (searchFilters.workKind) {
        params.append('work_kind', searchFilters.workKind);
      }
      if (searchFilters.majorCategory) {
        params.append('major_category', searchFilters.majorCategory);
      }
      if (searchFilters.photoType) {
        params.append('photo_type', searchFilters.photoType);
      }
      if (searchFilters.dateFrom) {
        params.append('date_from', searchFilters.dateFrom);
      }
      if (searchFilters.dateTo) {
        params.append('date_to', searchFilters.dateTo);
      }

      const response = await fetch(`${apiEndpoint}/api/v1/photos/search?${params.toString()}`);

      if (!response.ok) {
        throw new Error('検索に失敗しました');
      }

      const data = await response.json();
      setPhotos(data.items || []);
      setTotalResults(data.total || 0);
    } catch (err) {
      console.error('Search error:', err);
      setError('検索中にエラーが発生しました。もう一度お試しください。');
      setPhotos([]);
      setTotalResults(0);
    } finally {
      setIsLoading(false);
    }
  };

  // 初回ロード時にすべての写真を取得
  useEffect(() => {
    performSearch('', {});
  }, []);

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-7xl mx-auto w-full">
        <h1 className="text-3xl font-bold mb-2">写真検索</h1>
        <p className="text-gray-600 mb-8">
          キーワードやフィルターを使用して写真を検索できます。
        </p>

        <div className="space-y-4 mb-8">
          <SearchBar onSearch={handleSearch} />
          <FilterPanel onFilterChange={handleFilterChange} />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {totalResults}件の写真が見つかりました
              </p>
            </div>

            {photos.length > 0 ? (
              <PhotoGrid photos={photos} />
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
    </main>
  );
}
