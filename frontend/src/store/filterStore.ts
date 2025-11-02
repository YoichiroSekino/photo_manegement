/**
 * フィルター状態管理ストア
 */

import { create } from 'zustand';

export interface PhotoFilters {
  workType?: string;
  majorCategory?: string;
  photoType?: string;
  startDate?: string;
  endDate?: string;
  searchQuery?: string;
  location?: string;
  photographer?: string;
}

interface FilterStore {
  // State
  filters: PhotoFilters;
  isFilterOpen: boolean;

  // Actions
  setFilter: (key: keyof PhotoFilters, value: string | undefined) => void;
  setFilters: (filters: PhotoFilters) => void;
  clearFilters: () => void;
  clearFilter: (key: keyof PhotoFilters) => void;
  toggleFilterPanel: () => void;
  getActiveFilterCount: () => number;
}

export const useFilterStore = create<FilterStore>((set, get) => ({
  // Initial state
  filters: {},
  isFilterOpen: false,

  // Set single filter
  setFilter: (key, value) =>
    set((state) => ({
      filters: {
        ...state.filters,
        [key]: value,
      },
    })),

  // Set multiple filters
  setFilters: (filters) => set({ filters }),

  // Clear all filters
  clearFilters: () => set({ filters: {} }),

  // Clear single filter
  clearFilter: (key) =>
    set((state) => {
      const newFilters = { ...state.filters };
      delete newFilters[key];
      return { filters: newFilters };
    }),

  // Toggle filter panel
  toggleFilterPanel: () =>
    set((state) => ({ isFilterOpen: !state.isFilterOpen })),

  // Get count of active filters
  getActiveFilterCount: () => {
    const filters = get().filters;
    return Object.values(filters).filter((v) => v !== undefined && v !== '')
      .length;
  },
}));
