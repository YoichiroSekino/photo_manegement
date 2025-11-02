/**
 * フィルターパネルコンポーネント
 */

'use client';

import { useState } from 'react';

export interface FilterOptions {
  workType?: string;
  workKind?: string;
  majorCategory?: string;
  photoType?: string;
  dateFrom?: string;
  dateTo?: string;
}

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void;
  initialFilters?: FilterOptions;
}

// 工種オプション
const WORK_TYPES = [
  '基礎工',
  '土工',
  '配筋工',
  '型枠工',
  'コンクリート工',
  '鉄筋工',
  '舗装工',
  'その他',
];

// 写真大分類オプション
const MAJOR_CATEGORIES = [
  '着手前及び完成写真',
  '施工状況写真',
  '安全管理写真',
  '使用材料写真',
  '品質管理写真',
  '出来形管理写真',
  '災害写真',
  '事故写真',
  'その他',
];

// 写真区分オプション
const PHOTO_TYPES = [
  '工事全景',
  '作業状況',
  '安全対策',
  '品質管理',
  '出来形管理',
  '材料検収',
  'その他',
];

export function FilterPanel({ onFilterChange, initialFilters = {} }: FilterPanelProps) {
  const [filters, setFilters] = useState<FilterOptions>(initialFilters);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key: keyof FilterOptions, value: string) => {
    const newFilters = {
      ...filters,
      [key]: value || undefined,
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({});
    onFilterChange({});
  };

  const activeFilterCount = Object.values(filters).filter(v => v).length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50"
      >
        <div className="flex items-center space-x-2">
          <svg
            className="w-5 h-5 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          <span className="font-medium text-gray-900">フィルター</span>
          {activeFilterCount > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {activeFilterCount}
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${
            isExpanded ? 'transform rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 py-4 border-t border-gray-200 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* 工種 */}
            <div>
              <label htmlFor="workType" className="block text-sm font-medium text-gray-700 mb-1">
                工種
              </label>
              <select
                id="workType"
                value={filters.workType || ''}
                onChange={(e) => handleFilterChange('workType', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">すべて</option>
                {WORK_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* 写真大分類 */}
            <div>
              <label htmlFor="majorCategory" className="block text-sm font-medium text-gray-700 mb-1">
                写真大分類
              </label>
              <select
                id="majorCategory"
                value={filters.majorCategory || ''}
                onChange={(e) => handleFilterChange('majorCategory', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">すべて</option>
                {MAJOR_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            {/* 写真区分 */}
            <div>
              <label htmlFor="photoType" className="block text-sm font-medium text-gray-700 mb-1">
                写真区分
              </label>
              <select
                id="photoType"
                value={filters.photoType || ''}
                onChange={(e) => handleFilterChange('photoType', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">すべて</option>
                {PHOTO_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* 撮影日（開始） */}
            <div>
              <label htmlFor="dateFrom" className="block text-sm font-medium text-gray-700 mb-1">
                撮影日（開始）
              </label>
              <input
                type="date"
                id="dateFrom"
                value={filters.dateFrom || ''}
                onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* 撮影日（終了） */}
            <div>
              <label htmlFor="dateTo" className="block text-sm font-medium text-gray-700 mb-1">
                撮影日（終了）
              </label>
              <input
                type="date"
                id="dateTo"
                value={filters.dateTo || ''}
                onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          {/* クリアボタン */}
          {activeFilterCount > 0 && (
            <div className="flex justify-end">
              <button
                onClick={handleClearFilters}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg
                  className="mr-2 -ml-0.5 h-4 w-4"
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
                フィルターをクリア
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
