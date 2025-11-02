/**
 * 写真データの型定義
 */

export interface Photo {
  id: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  s3Url?: string;
  thumbnailUrl?: string;
  title?: string;
  description?: string;
  shootingDate?: string;
  location?: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  category?: PhotoCategory;
  tags?: string[];
  metadata?: PhotoMetadata;
  createdAt: string;
  updatedAt: string;
}

export interface PhotoCategory {
  majorCategory: '工事' | '測量' | '調査' | '地質' | '広報' | '設計' | 'その他';
  photoType:
    | '着手前及び完成写真'
    | '施工状況写真'
    | '安全管理写真'
    | '使用材料写真'
    | '品質管理写真'
    | '出来形管理写真'
    | '災害写真'
    | '事故写真'
    | 'その他';
  workType?: string; // 工種
  workKind?: string; // 種別
  workDetail?: string; // 細別
}

export interface QualityIssue {
  type: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  recommendation?: string;
}

export interface PhotoMetadata {
  width: number;
  height: number;
  pixelCount: number;
  exif?: {
    make?: string;
    model?: string;
    dateTime?: string;
    gpsLatitude?: number;
    gpsLongitude?: number;
  };
  blackboard?: {
    text: string;
    confidence: number;
  };
  quality?: {
    sharpness: number;
    brightness: number;
    contrast: number;
    score?: number;
    grade?: 'excellent' | 'good' | 'fair' | 'poor';
    issues?: string[];
    recommendations?: string[];
  };
}

export interface UploadFile extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface UploadProgress {
  fileId: string;
  fileName: string;
  progress: number;
  uploadedBytes: number;
  totalBytes: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}
