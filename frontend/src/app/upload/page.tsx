'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useProjects } from '@/hooks/useProjects';
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
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatuses, setUploadStatuses] = useState<Map<string, FileUploadStatus>>(new Map());

  // 最初のプロジェクトを自動選択
  useEffect(() => {
    if (projects && projects.length > 0 && !selectedProjectId) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

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

    if (!selectedProjectId) {
      setErrors(['プロジェクトを選択してください。']);
      return;
    }

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
      const accessToken = localStorage.getItem('access_token');

      // モックアップロードエンドポイントを使用
      const mockUploadEndpoint = `${apiEndpoint}/api/v1/photos/mock-upload`;

      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];

        // ステータス更新: uploading
        setUploadStatuses((prev) => {
          const newStatuses = new Map(prev);
          const status = newStatuses.get(file.name);
          if (status) {
            status.progress = { ...status.progress, status: 'uploading', percentage: 50 };
            newStatuses.set(file.name, { ...status });
          }
          return newStatuses;
        });

        try {
          // フォームデータ作成
          const formData = new FormData();
          formData.append('file', file);
          formData.append('project_id', selectedProjectId.toString());

          // アップロード
          const response = await fetch(mockUploadEndpoint, {
            method: 'POST',
            headers: {
              ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
            },
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed for ${file.name}`);
          }

          // ステータス更新: completed
          setUploadStatuses((prev) => {
            const newStatuses = new Map(prev);
            const status = newStatuses.get(file.name);
            if (status) {
              status.progress = { ...status.progress, status: 'completed', percentage: 100 };
              newStatuses.set(file.name, { ...status });
            }
            return newStatuses;
          });
        } catch (error) {
          console.error(`Upload error for ${file.name}:`, error);
          // ステータス更新: error
          setUploadStatuses((prev) => {
            const newStatuses = new Map(prev);
            const status = newStatuses.get(file.name);
            if (status) {
              status.progress = { ...status.progress, status: 'error', error: 'アップロード失敗' };
              newStatuses.set(file.name, { ...status });
            }
            return newStatuses;
          });
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
  }, [selectedFiles, selectedProjectId]);

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-4xl mx-auto w-full">
        <h1 className="text-3xl font-bold mb-2">写真アップロード</h1>
        <p className="text-gray-600 mb-8">
          工事写真をドラッグ&ドロップまたは選択してアップロードしてください。
        </p>

        {/* プロジェクト選択 */}
        <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg">
          <label htmlFor="project-select" className="block text-sm font-medium text-gray-700 mb-2">
            アップロード先プロジェクト <span className="text-red-500">*</span>
          </label>
          {projectsLoading ? (
            <div className="text-sm text-gray-500">プロジェクトを読み込み中...</div>
          ) : projects && projects.length > 0 ? (
            <select
              id="project-select"
              value={selectedProjectId || ''}
              onChange={(e) => setSelectedProjectId(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="" disabled>プロジェクトを選択</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          ) : (
            <div className="text-sm text-amber-600">
              プロジェクトがありません。
              <a href="/projects/new" className="text-blue-600 hover:underline ml-2">
                新しいプロジェクトを作成
              </a>
            </div>
          )}
        </div>

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
              disabled={isUploading || !selectedProjectId}
              className="mt-4 w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'アップロード中...' : !selectedProjectId ? 'プロジェクトを選択してください' : 'アップロード開始'}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
