/**
 * 写真データ操作用カスタムフック
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPost, apiPatch, apiDelete, ApiError } from '@/lib/apiClient';
import { useUIStore } from '@/store/uiStore';
import { Photo } from '@/types/photo';

// API Response Types (Backend)
export interface PhotoAPIResponse {
  id: number;
  file_name: string;
  s3_key: string;
  s3_url?: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  taken_date?: string | null;
  shooting_date?: string | null;
  location?: string | null;
  location_address?: string | null;
  gps_latitude?: number | null;
  latitude?: number | null;
  gps_longitude?: number | null;
  longitude?: number | null;
  photographer?: string | null;
  work_type?: string | null;
  major_category?: string | null;
  photo_type?: string | null;
  photo_title?: string | null;
  title?: string | null;
  description?: string | null;
  is_representative?: boolean;
  ocr_text?: string | null;
  ocr_confidence?: number | null;
  ai_labels?: string[] | null;
  tags?: string[] | null;
  quality_score?: number | null;
  brightness_score?: number | null;
  contrast_score?: number | null;
  quality_grade?: string | null;
  quality_issues?: string[] | null;
  quality_recommendations?: string[] | null;
  is_duplicate?: boolean;
  duplicate_group_id?: string | null;
  created_at: string;
  updated_at: string;
  organization_id: number;
}

export interface PhotoListAPIResponse {
  items: PhotoAPIResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PhotoSearchParams {
  workType?: string;
  majorCategory?: string;
  photoType?: string;
  startDate?: string;
  endDate?: string;
  searchQuery?: string;
  location?: string;
  photographer?: string;
  skip?: number;
  limit?: number;
}

export interface PhotoCreateInput {
  file_name: string;
  s3_key: string;
  s3_url: string;
  file_size: number;
  mime_type: string;
  width: number;
  height: number;
  taken_date?: string;
  location?: string;
  gps_latitude?: number;
  gps_longitude?: number;
  photographer?: string;
  project_id: number;
}

export interface PhotoUpdateInput {
  work_type?: string;
  major_category?: string;
  photo_type?: string;
  photo_title?: string;
  description?: string;
  is_representative?: boolean;
  location?: string;
  photographer?: string;
}

// Map API response to frontend Photo type
function mapAPIResponseToPhoto(apiPhoto: PhotoAPIResponse): Photo {
  const latitude = apiPhoto.latitude ?? apiPhoto.gps_latitude;
  const longitude = apiPhoto.longitude ?? apiPhoto.gps_longitude;
  const width = apiPhoto.width ?? 0;
  const height = apiPhoto.height ?? 0;

  return {
    id: String(apiPhoto.id),
    fileName: apiPhoto.file_name,
    fileSize: apiPhoto.file_size,
    mimeType: apiPhoto.mime_type,
    s3Url: apiPhoto.s3_url ?? `https://${process.env.NEXT_PUBLIC_S3_BUCKET || 'construction-photos-dev'}.s3.${process.env.NEXT_PUBLIC_AWS_REGION || 'ap-northeast-1'}.amazonaws.com/${apiPhoto.s3_key}`,
    title: apiPhoto.title ?? apiPhoto.photo_title ?? undefined,
    description: apiPhoto.description ?? undefined,
    shootingDate: apiPhoto.shooting_date ?? apiPhoto.taken_date ?? undefined,
    location: latitude && longitude
      ? {
          latitude,
          longitude,
          address: apiPhoto.location_address ?? apiPhoto.location ?? undefined,
        }
      : undefined,
    category: apiPhoto.major_category || apiPhoto.photo_type || apiPhoto.work_type
      ? {
          majorCategory: (apiPhoto.major_category as any) || 'その他',
          photoType: (apiPhoto.photo_type as any) || 'その他',
          workType: apiPhoto.work_type || undefined,
        }
      : undefined,
    tags: apiPhoto.tags ?? apiPhoto.ai_labels ?? undefined,
    metadata: {
      width,
      height,
      pixelCount: width * height,
      blackboard: apiPhoto.ocr_text && apiPhoto.ocr_confidence
        ? {
            text: apiPhoto.ocr_text,
            confidence: apiPhoto.ocr_confidence,
          }
        : undefined,
      quality: apiPhoto.quality_score
        ? {
            sharpness: apiPhoto.quality_score,
            brightness: apiPhoto.brightness_score || 0,
            contrast: apiPhoto.contrast_score || 0,
            score: Math.round(apiPhoto.quality_score * 100),
            grade: apiPhoto.quality_grade as 'excellent' | 'good' | 'fair' | 'poor',
            issues: apiPhoto.quality_issues || [],
            recommendations: apiPhoto.quality_recommendations || [],
          }
        : undefined,
    },
    createdAt: apiPhoto.created_at,
    updatedAt: apiPhoto.updated_at,
  };
}

// Query keys
export const photoKeys = {
  all: ['photos'] as const,
  lists: () => [...photoKeys.all, 'list'] as const,
  list: (filters: PhotoSearchParams) =>
    [...photoKeys.lists(), filters] as const,
  details: () => [...photoKeys.all, 'detail'] as const,
  detail: (id: number) => [...photoKeys.details(), id] as const,
};

/**
 * 写真一覧取得（ページネーション付き）
 */
export function usePhotos(params: PhotoSearchParams & { page?: number; page_size?: number } = {}) {
  const addNotification = useUIStore((state) => state.addNotification);

  return useQuery({
    queryKey: photoKeys.list(params),
    queryFn: async () => {
      try {
        const queryParams = new URLSearchParams();

        // ページネーションパラメータ
        if (params.page) queryParams.append('page', String(params.page));
        if (params.page_size) queryParams.append('page_size', String(params.page_size));

        // その他のパラメータ
        Object.entries(params).forEach(([key, value]) => {
          if (key !== 'page' && key !== 'page_size' && value !== undefined && value !== null && value !== '') {
            queryParams.append(key, String(value));
          }
        });

        const endpoint = `/api/v1/photos${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
        const response = await apiGet<PhotoListAPIResponse>(endpoint);

        return {
          photos: response.items.map(mapAPIResponseToPhoto),
          total: response.total,
          page: response.page,
          page_size: response.page_size,
          total_pages: response.total_pages,
        };
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `写真の取得に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
  });
}

/**
 * 写真詳細取得
 */
export function usePhoto(photoId: number | null) {
  const addNotification = useUIStore((state) => state.addNotification);

  return useQuery({
    queryKey: photoKeys.detail(photoId!),
    queryFn: async () => {
      try {
        const apiPhoto = await apiGet<PhotoAPIResponse>(`/api/v1/photos/${photoId}`);
        return mapAPIResponseToPhoto(apiPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `写真の取得に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    enabled: photoId !== null,
  });
}

/**
 * 写真検索
 */
export function useSearchPhotos() {
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (params: PhotoSearchParams) => {
      try {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            queryParams.append(key, String(value));
          }
        });

        const apiPhotos = await apiGet<PhotoAPIResponse[]>(
          `/api/v1/photos/search?${queryParams.toString()}`
        );
        return apiPhotos.map(mapAPIResponseToPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `検索に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
  });
}

/**
 * 写真作成
 */
export function useCreatePhoto() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (data: PhotoCreateInput) => {
      try {
        const apiPhoto = await apiPost<PhotoAPIResponse>('/api/v1/photos', data);
        return mapAPIResponseToPhoto(apiPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `写真の登録に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: photoKeys.lists() });
      addNotification('success', '写真を登録しました');
    },
  });
}

/**
 * 写真更新
 */
export function useUpdatePhoto() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async ({
      photoId,
      data,
    }: {
      photoId: number;
      data: PhotoUpdateInput;
    }) => {
      try {
        const apiPhoto = await apiPatch<PhotoAPIResponse>(`/api/v1/photos/${photoId}`, data);
        return mapAPIResponseToPhoto(apiPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `写真の更新に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: photoKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: photoKeys.detail(variables.photoId),
      });
      addNotification('success', '写真を更新しました');
    },
  });
}

/**
 * 写真削除
 */
export function useDeletePhoto() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (photoId: number) => {
      try {
        return await apiDelete<void>(`/api/v1/photos/${photoId}`);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `写真の削除に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: photoKeys.lists() });
      addNotification('success', '写真を削除しました');
    },
  });
}

/**
 * OCR処理実行
 */
export function useProcessOCR() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (photoId: number) => {
      try {
        const apiPhoto = await apiPost<PhotoAPIResponse>(`/api/v1/photos/${photoId}/process-ocr`);
        return mapAPIResponseToPhoto(apiPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `OCR処理に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: (_, photoId) => {
      queryClient.invalidateQueries({ queryKey: photoKeys.detail(photoId) });
      addNotification('success', 'OCR処理が完了しました');
    },
  });
}

/**
 * AI分類実行
 */
export function useClassifyPhoto() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (photoId: number) => {
      try {
        const apiPhoto = await apiPost<PhotoAPIResponse>(`/api/v1/photos/${photoId}/classify`);
        return mapAPIResponseToPhoto(apiPhoto);
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `AI分類に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: (_, photoId) => {
      queryClient.invalidateQueries({ queryKey: photoKeys.detail(photoId) });
      addNotification('success', 'AI分類が完了しました');
    },
  });
}

/**
 * 重複検出実行
 */
export function useDetectDuplicates() {
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (params: { similarity_threshold?: number } = {}) => {
      try {
        const threshold = params.similarity_threshold || 90.0;
        const response = await apiPost<{
          total_photos: number;
          duplicate_groups: Array<{
            group_id: number;
            photos: Array<{
              id: number;
              file_name: string;
              phash: string;
              similarity?: number;
            }>;
            avg_similarity: number;
            photo_count: number;
          }>;
          summary: {
            total_groups: number;
            total_duplicate_photos: number;
            avg_similarity: number;
            largest_group_size: number;
          };
        }>(`/api/v1/photos/detect-duplicates?similarity_threshold=${threshold}`);
        return response;
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `重複検出に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: (data) => {
      const groupCount = data.duplicate_groups.length;
      if (groupCount > 0) {
        addNotification('success', `${groupCount}件の重複グループが見つかりました`);
      } else {
        addNotification('info', '重複写真は見つかりませんでした');
      }
    },
  });
}

/**
 * 品質評価実行
 */
export function useAssessQuality() {
  const queryClient = useQueryClient();
  const addNotification = useUIStore((state) => state.addNotification);

  return useMutation({
    mutationFn: async (photoId: number) => {
      try {
        const response = await apiPost<{
          photo_id: number;
          sharpness: number;
          brightness: number;
          contrast: number;
          quality_score: number;
          quality_grade: string;
          issues: string[];
          recommendations: string[];
          status: string;
        }>(`/api/v1/photos/${photoId}/assess-quality`);
        return response;
      } catch (error) {
        if (error instanceof ApiError) {
          addNotification('error', `品質評価に失敗しました: ${error.message}`);
        }
        throw error;
      }
    },
    onSuccess: (data, photoId) => {
      queryClient.invalidateQueries({ queryKey: photoKeys.detail(photoId) });
      queryClient.invalidateQueries({ queryKey: photoKeys.lists() });
      addNotification('success', `品質評価が完了しました（スコア: ${data.quality_score}）`);
    },
  });
}
