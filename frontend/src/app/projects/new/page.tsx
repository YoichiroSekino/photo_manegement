'use client';

import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout';
import ProjectForm from '@/components/Projects/ProjectForm';

export default function NewProjectPage() {
  return (
    <AuthenticatedLayout>
      <div className="container mx-auto px-4 py-8">
        <ProjectForm mode="create" />
      </div>
    </AuthenticatedLayout>
  );
}
