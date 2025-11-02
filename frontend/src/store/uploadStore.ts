/**
 * アップロード状態管理ストア
 */

import { create } from 'zustand';

export interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  progress: number;
  error?: string;
  s3Key?: string;
}

interface UploadStore {
  // State
  files: UploadFile[];
  isUploading: boolean;
  uploadedCount: number;
  totalCount: number;

  // Actions
  addFiles: (files: File[]) => void;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;
  updateFileStatus: (
    fileId: string,
    status: UploadFile['status'],
    progress?: number,
    error?: string,
    s3Key?: string
  ) => void;
  setIsUploading: (isUploading: boolean) => void;
  resetUpload: () => void;
}

export const useUploadStore = create<UploadStore>((set) => ({
  // Initial state
  files: [],
  isUploading: false,
  uploadedCount: 0,
  totalCount: 0,

  // Add files to upload queue
  addFiles: (newFiles: File[]) =>
    set((state) => {
      const uploadFiles: UploadFile[] = newFiles.map((file) => ({
        id: `${file.name}-${Date.now()}-${Math.random()}`,
        file,
        status: 'pending',
        progress: 0,
      }));
      return {
        files: [...state.files, ...uploadFiles],
        totalCount: state.totalCount + newFiles.length,
      };
    }),

  // Remove a file from queue
  removeFile: (fileId: string) =>
    set((state) => ({
      files: state.files.filter((f) => f.id !== fileId),
      totalCount: state.files.filter((f) => f.id !== fileId).length,
      uploadedCount: state.files.filter(
        (f) => f.id !== fileId && f.status === 'completed'
      ).length,
    })),

  // Clear all files
  clearFiles: () =>
    set({
      files: [],
      uploadedCount: 0,
      totalCount: 0,
    }),

  // Update file upload status
  updateFileStatus: (fileId, status, progress, error, s3Key) =>
    set((state) => {
      const updatedFiles = state.files.map((f) =>
        f.id === fileId
          ? {
              ...f,
              status,
              progress: progress ?? f.progress,
              error,
              s3Key: s3Key ?? f.s3Key,
            }
          : f
      );

      const uploadedCount = updatedFiles.filter(
        (f) => f.status === 'completed'
      ).length;

      return {
        files: updatedFiles,
        uploadedCount,
      };
    }),

  // Set uploading state
  setIsUploading: (isUploading: boolean) => set({ isUploading }),

  // Reset upload state
  resetUpload: () =>
    set({
      files: [],
      isUploading: false,
      uploadedCount: 0,
      totalCount: 0,
    }),
}));
