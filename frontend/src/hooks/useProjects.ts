/**
 * プロジェクト関連のカスタムフック
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { Project, ProjectCreate, ProjectUpdate, ProjectStats } from '@/types/project';

/**
 * プロジェクト一覧を取得
 */
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      return await apiClient.get<Project[]>('/api/v1/projects');
    },
  });
}

/**
 * プロジェクト詳細を取得
 */
export function useProject(projectId: number | undefined) {
  return useQuery({
    queryKey: ['projects', projectId],
    queryFn: async () => {
      if (!projectId) throw new Error('Project ID is required');
      return await apiClient.get<Project>(`/api/v1/projects/${projectId}`);
    },
    enabled: !!projectId,
  });
}

/**
 * プロジェクト統計情報を取得
 */
export function useProjectStats(projectId: number | undefined) {
  return useQuery({
    queryKey: ['projects', projectId, 'stats'],
    queryFn: async () => {
      if (!projectId) throw new Error('Project ID is required');
      return await apiClient.get<ProjectStats>(`/api/v1/projects/${projectId}/stats`);
    },
    enabled: !!projectId,
  });
}

/**
 * プロジェクトを作成
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ProjectCreate) => {
      return await apiClient.post<Project>('/api/v1/projects', data);
    },
    onSuccess: () => {
      // プロジェクト一覧をリフレッシュ
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * プロジェクトを更新
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: ProjectUpdate }) => {
      return await apiClient.patch<Project>(`/api/v1/projects/${id}`, data);
    },
    onSuccess: (_, variables) => {
      // プロジェクト一覧と詳細をリフレッシュ
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['projects', variables.id] });
    },
  });
}

/**
 * プロジェクトを削除
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/projects/${id}`);
    },
    onSuccess: () => {
      // プロジェクト一覧をリフレッシュ
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
