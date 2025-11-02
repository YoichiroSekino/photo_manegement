'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { DragDropZone } from '@/components/upload/DragDropZone';
import { validateFiles, getValidFiles, getErrorMessages } from '@/lib/fileValidator';
import { PresignedUploader, UploadProgress } from '@/lib/s3Upload';

interface FileUploadStatus {
  file: File;
  progress: UploadProgress;
}

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatuses, setUploadStatuses] = useState<Map<string, FileUploadStatus>>(new Map());

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  const handleFilesSelected = useCallback((files: File[]) => {
    // ファイルバリデーション
    const results = validateFiles(files);
    const validFiles = getValidFiles(results);
    const errorMessages = getErrorMessages(results);

    setSelectedFiles(validFiles);
    setErrors(errorMessages);

    // アップロード状態をリセット
    setUploadStatuses(new Map());
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setErrors([]);

    const statuses = new Map<string, FileUploadStatus>();
    selectedFiles.forEach((file) => {
      statuses.set(file.name, {
        file,
        progress: {
          fileName: file.name,
          loaded: 0,
          total: file.size,
          percentage: 0,
          status: 'pending',
        },
      });
    });
    setUploadStatuses(new Map(statuses));

    try {
      const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const uploadEndpoint = `${apiEndpoint}/api/v1/photos/upload`;

      // 認証トークン取得
      const accessToken = localStorage.getItem('access_token');

      const uploadResults = await PresignedUploader.uploadMultipleWithPresignedUrl(
        selectedFiles,
        uploadEndpoint,
        (fileName, progress) => {
          setUploadStatuses((prev) => {
            const newStatuses = new Map(prev);
            const status = newStatuses.get(fileName);
            if (status) {
              status.progress = progress;
              newStatuses.set(fileName, { ...status });
            }
            return newStatuses;
          });
        },
        5, // 最大5並列
        accessToken || undefined
      );

      // S3アップロード成功後、写真レコードを作成
      const createPhotoEndpoint = `${apiEndpoint}/api/v1/photos`;
      for (let i = 0; i < uploadResults.length; i++) {
        const result = uploadResults[i];
        const file = selectedFiles[i];

        try {
          const response = await fetch(createPhotoEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
            },
            body: JSON.stringify({
              file_name: file.name,
              file_size: file.size,
              mime_type: file.type,
              s3_key: result.key,
            }),
          });

          if (!response.ok) {
            console.error(`Failed to create photo record for ${file.name}`);
          }
        } catch (error) {
          console.error(`Error creating photo record for ${file.name}:`, error);
        }
      }

      // アップロード成功
      console.log('All files uploaded successfully');
      setTimeout(() => {
        setSelectedFiles([]);
        setUploadStatuses(new Map());
      }, 2000);
    } catch (error) {
      console.error('Upload error:', error);
      setErrors(['アップロード中にエラーが発生しました。もう一度お試しください。']);
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
                {selectedFiles.map((file, index) => {
                  const status = uploadStatuses.get(file.name);
                  const progress = status?.progress;

                  return (
                    <li
                      key={index}
                      className="px-4 py-3 hover:bg-gray-50"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3 flex-1">
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
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        {progress && (
                          <div className="ml-4 flex items-center space-x-2">
                            {progress.status === 'uploading' && (
                              <span className="text-sm text-blue-600">
                                {progress.percentage}%
                              </span>
                            )}
                            {progress.status === 'completed' && (
                              <svg
                                className="w-5 h-5 text-green-500"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M5 13l4 4L19 7"
                                />
                              </svg>
                            )}
                            {progress.status === 'error' && (
                              <svg
                                className="w-5 h-5 text-red-500"
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
                            )}
                          </div>
                        )}
                      </div>
                      {progress && progress.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress.percentage}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {progress && progress.status === 'error' && progress.error && (
                        <p className="mt-1 text-xs text-red-600">{progress.error}</p>
                      )}
                    </li>
                  );
                })}
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
