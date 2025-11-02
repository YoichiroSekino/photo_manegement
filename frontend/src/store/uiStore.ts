/**
 * UI状態管理ストア
 */

import { create } from 'zustand';

export type ViewMode = 'grid' | 'list';
export type SortField = 'date' | 'name' | 'category' | 'quality';
export type SortOrder = 'asc' | 'desc';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface UIStore {
  // State
  viewMode: ViewMode;
  sortField: SortField;
  sortOrder: SortOrder;
  selectedPhotoIds: Set<number>;
  notifications: Notification[];
  isLoading: boolean;

  // Actions
  setViewMode: (mode: ViewMode) => void;
  setSorting: (field: SortField, order: SortOrder) => void;
  togglePhotoSelection: (photoId: number) => void;
  selectAllPhotos: (photoIds: number[]) => void;
  clearSelection: () => void;
  addNotification: (
    type: Notification['type'],
    message: string,
    duration?: number
  ) => void;
  removeNotification: (id: string) => void;
  setIsLoading: (isLoading: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  // Initial state
  viewMode: 'grid',
  sortField: 'date',
  sortOrder: 'desc',
  selectedPhotoIds: new Set(),
  notifications: [],
  isLoading: false,

  // Set view mode (grid/list)
  setViewMode: (mode: ViewMode) => set({ viewMode: mode }),

  // Set sorting
  setSorting: (field: SortField, order: SortOrder) =>
    set({ sortField: field, sortOrder: order }),

  // Toggle photo selection
  togglePhotoSelection: (photoId: number) =>
    set((state) => {
      const newSelection = new Set(state.selectedPhotoIds);
      if (newSelection.has(photoId)) {
        newSelection.delete(photoId);
      } else {
        newSelection.add(photoId);
      }
      return { selectedPhotoIds: newSelection };
    }),

  // Select all photos
  selectAllPhotos: (photoIds: number[]) =>
    set({ selectedPhotoIds: new Set(photoIds) }),

  // Clear selection
  clearSelection: () => set({ selectedPhotoIds: new Set() }),

  // Add notification
  addNotification: (type, message, duration = 5000) =>
    set((state) => {
      const id = `notification-${Date.now()}-${Math.random()}`;
      const notification: Notification = { id, type, message, duration };

      // Auto-remove notification after duration
      if (duration > 0) {
        setTimeout(() => {
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }));
        }, duration);
      }

      return {
        notifications: [...state.notifications, notification],
      };
    }),

  // Remove notification
  removeNotification: (id: string) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  // Set loading state
  setIsLoading: (isLoading: boolean) => set({ isLoading }),
}));
