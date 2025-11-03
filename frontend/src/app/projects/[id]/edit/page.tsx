'use client';

import { use } from 'react';
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout';
import ProjectForm from '@/components/Projects/ProjectForm';
import { useProject } from '@/hooks/useProjects';

export default function EditProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const projectId = parseInt(id);
  const { data: project, isLoading, error } = useProject(projectId);

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

  if (error || !project) {
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
        <ProjectForm mode="edit" project={project} />
      </div>
    </AuthenticatedLayout>
  );
}
