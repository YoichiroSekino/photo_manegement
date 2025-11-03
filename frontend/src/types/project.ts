/**
 * プロジェクト関連の型定義
 */

export interface Project {
  id: number;
  organization_id: number;
  name: string;
  description: string | null;
  client_name: string | null;
  start_date: string | null;
  end_date: string | null;
  photo_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  client_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
  client_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ProjectStats {
  project_id: number;
  photo_count: number;
  today_uploads: number;
  this_week_uploads: number;
  category_distribution: Record<string, number>;
  quality_issues_count: number;
}
