'use client';

import { useState } from 'react';
import { useProjects, useDeleteProject } from '@/hooks/useProjects';
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout';
import Link from 'next/link';
import { Project } from '@/types/project';

export default function ProjectsPage() {
  const { data: projects, isLoading, error } = useProjects();
  const deleteProject = useDeleteProject();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (project: Project) => {
    if (!confirm(`プロジェクト「${project.name}」を削除しますか？\n※写真が紐づいている場合は削除できません。`)) {
      return;
    }

    setDeletingId(project.id);
    try {
      await deleteProject.mutateAsync(project.id);
      alert('プロジェクトを削除しました');
    } catch (error: any) {
      alert(error.message || 'プロジェクトの削除に失敗しました');
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <AuthenticatedLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">読み込み中...</p>
          </div>
        </div>
      </AuthenticatedLayout>
    );
  }

  if (error) {
    return (
      <AuthenticatedLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-red-600">プロジェクトの取得に失敗しました</p>
          </div>
        </div>
      </AuthenticatedLayout>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">プロジェクト管理</h1>
            <p className="text-gray-600 mt-2">工事プロジェクトの一覧と管理</p>
          </div>
          <Link
            href="/projects/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            + 新規プロジェクト
          </Link>
        </div>

        {/* Projects List */}
        {!projects || projects.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">プロジェクトがありません</h3>
            <p className="mt-1 text-sm text-gray-500">
              新しいプロジェクトを作成して、写真を整理しましょう
            </p>
            <div className="mt-6">
              <Link
                href="/projects/new"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                + 新規プロジェクト
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 flex-1">
                    {project.name}
                  </h3>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    {project.photo_count} 枚
                  </span>
                </div>

                {project.client_name && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">クライアント:</span> {project.client_name}
                  </p>
                )}

                {project.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}

                {(project.start_date || project.end_date) && (
                  <div className="text-xs text-gray-500 mb-4">
                    {project.start_date && (
                      <div>開始: {new Date(project.start_date).toLocaleDateString('ja-JP')}</div>
                    )}
                    {project.end_date && (
                      <div>終了: {new Date(project.end_date).toLocaleDateString('ja-JP')}</div>
                    )}
                  </div>
                )}

                <div className="flex gap-2 mt-4 pt-4 border-t">
                  <Link
                    href={`/projects/${project.id}`}
                    className="flex-1 text-center bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm font-medium"
                  >
                    詳細
                  </Link>
                  <Link
                    href={`/projects/${project.id}/edit`}
                    className="flex-1 text-center bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300 text-sm font-medium"
                  >
                    編集
                  </Link>
                  <button
                    onClick={() => handleDelete(project)}
                    disabled={deletingId === project.id}
                    className="bg-red-100 text-red-700 px-4 py-2 rounded hover:bg-red-200 text-sm font-medium disabled:opacity-50"
                  >
                    {deletingId === project.id ? '削除中...' : '削除'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AuthenticatedLayout>
  );
}
