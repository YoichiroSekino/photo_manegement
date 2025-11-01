'use client';

import { useState, useCallback } from 'react';
import { DragDropZone } from '@/components/upload/DragDropZone';
import { validateFiles, getValidFiles, getErrorMessages } from '@/lib/fileValidator';

export default function UploadPage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFilesSelected = useCallback((files: File[]) => {
    // ファイルバリデーション
    const results = validateFiles(files);
    const validFiles = getValidFiles(results);
    const errorMessages = getErrorMessages(results);

    setSelectedFiles(validFiles);
    setErrors(errorMessages);
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    try {
      // TODO: S3アップロード実装
      console.log('Uploading files:', selectedFiles);
      await new Promise((resolve) => setTimeout(resolve, 2000)); // 模擬アップロード
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFiles]);

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-4xl mx-auto w-full">
        <h1 className="text-3xl font-bold mb-2">写真アップロード</h1>
        <p className="text-gray-600 mb-8">
          工事写真をドラッグ&ドロップまたは選択してアップロードしてください。
        </p>

        <DragDropZone onFilesSelected={handleFilesSelected} />

        {errors.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-sm font-semibold text-red-800 mb-2">
              エラーが発生しました：
            </h3>
            <ul className="text-sm text-red-700 space-y-1">
              {errors.map((error, index) => (
                <li key={index}>• {error}</li>
              ))}
            </ul>
          </div>
        )}

        {selectedFiles.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">
              選択されたファイル ({selectedFiles.length}件)
            </h2>
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <ul className="divide-y divide-gray-200">
                {selectedFiles.map((file, index) => (
                  <li
                    key={index}
                    className="px-4 py-3 flex items-center justify-between hover:bg-gray-50"
                  >
                    <div className="flex items-center space-x-3">
                      <svg
                        className="w-8 h-8 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="mt-4 w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'アップロード中...' : 'アップロード開始'}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
