# 技術アーキテクチャ設計書

**バージョン**: 1.0
**作成日**: 2025-11-02
**対象システム**: 工事写真自動整理システム

---

## 目次

1. [アーキテクチャ概要](#1-アーキテクチャ概要)
2. [システム構成図](#2-システム構成図)
3. [フロントエンド設計](#3-フロントエンド設計)
4. [バックエンド設計](#4-バックエンド設計)
5. [データベース設計](#5-データベース設計)
6. [AI/ML基盤設計](#6-aiml基盤設計)
7. [インフラストラクチャ設計](#7-インフラストラクチャ設計)
8. [API設計](#8-api設計)
9. [セキュリティ設計](#9-セキュリティ設計)
10. [スケーラビリティ設計](#10-スケーラビリティ設計)

---

## 1. アーキテクチャ概要

### 1.1 アーキテクチャスタイル

**サーバーレス + マイクロサービス アーキテクチャ**

```
┌─────────────────────────────────────────────────────────────┐
│                      ユーザー                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   CloudFront (CDN)                           │
│              • Global edge locations                         │
│              • SSL/TLS termination                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              フロントエンド (Next.js PWA)                      │
│              • S3 + CloudFront hosting                       │
│              • Static Site Generation (SSG)                 │
│              • Progressive Web App                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (REST + WebSocket)                  │
│              • Request validation                            │
│              • Rate limiting                                 │
│              • API key management                           │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Lambda     │    │   Lambda     │    │   Lambda     │
│  (Upload)    │    │ (Processing) │    │  (Search)    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    データ層                                   │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌────────┐       │
│  │   S3    │  │   RDS   │  │  Redis   │  │  SQS   │       │
│  │(写真)    │  │(メタ)    │  │(キャッシュ)│  │(Queue) │       │
│  └─────────┘  └─────────┘  └──────────┘  └────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI/ML 層                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐        │
│  │  Textract    │  │ Rekognition  │  │ SageMaker  │        │
│  │   (OCR)      │  │ (画像認識)     │  │ (カスタム)  │        │
│  └──────────────┘  └──────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 設計原則

1. **疎結合**: マイクロサービス間の依存を最小化
2. **イベント駆動**: SQS/EventBridgeによる非同期処理
3. **スケーラビリティ**: 自動スケーリング対応
4. **コスト最適化**: サーバーレスで従量課金
5. **高可用性**: Multi-AZ構成

### 1.3 技術スタック

| レイヤー | 技術 | 選定理由 |
|---------|------|---------|
| **フロントエンド** | Next.js 14, TypeScript, Tailwind CSS | SSG/SSR対応、型安全性、開発効率 |
| **バックエンド** | Node.js (Lambda), FastAPI (Python) | サーバーレス適合、AI/ML統合容易 |
| **データベース** | PostgreSQL (RDS), Redis (ElastiCache) | JSONB対応、高速キャッシュ |
| **ストレージ** | S3, CloudFront | 大容量対応、低コスト、CDN |
| **AI/ML** | Textract, Rekognition, SageMaker | マネージドML、高精度 |
| **認証** | AWS Cognito | OAuth2.0、SAML対応 |
| **監視** | CloudWatch, X-Ray | AWS統合監視 |

---

## 2. システム構成図

### 2.1 全体構成図（詳細）

```
Internet
    │
    ├──▶ Route 53 (DNS)
    │        │
    │        ▼
    └──▶ CloudFront Distribution
             │
             ├──▶ S3 Bucket (Next.js Static Files)
             │     • HTML, CSS, JS
             │     • Images, Fonts
             │
             └──▶ API Gateway
                     │
                     ├──▶ /api/v1/photos/*
                     │       └─▶ Lambda (Photo Service)
                     │              ├─▶ S3 (presigned URL)
                     │              ├─▶ RDS (metadata)
                     │              └─▶ SQS (async processing)
                     │
                     ├──▶ /api/v1/ai/*
                     │       └─▶ Lambda (AI Service)
                     │              ├─▶ Textract (OCR)
                     │              ├─▶ Rekognition (分類)
                     │              └─▶ SageMaker (カスタムモデル)
                     │
                     └──▶ /api/v1/export/*
                             └─▶ Lambda (Export Service)
                                    └─▶ S3 (XML生成)

VPC (10.0.0.0/16)
    │
    ├──▶ Public Subnet (10.0.1.0/24)
    │       └─▶ NAT Gateway
    │
    ├──▶ Private Subnet 1 (10.0.10.0/24)
    │       ├─▶ RDS Primary (PostgreSQL 15)
    │       └─▶ ElastiCache (Redis)
    │
    └──▶ Private Subnet 2 (10.0.11.0/24)
            └─▶ RDS Standby (Multi-AZ)

Background Processing
    │
    ├──▶ SQS Queue (Photo Processing)
    │       └─▶ Lambda (Processor)
    │              ├─▶ Textract
    │              ├─▶ Rekognition
    │              └─▶ RDS (update)
    │
    └──▶ EventBridge Rules
            └─▶ Lambda (Scheduled Tasks)
```

### 2.2 データフロー

#### 写真アップロードフロー

```
User → CloudFront → S3 (Direct Upload)
  │
  └─▶ API Gateway → Lambda (CreatePhotoMetadata)
                       │
                       ├─▶ RDS (INSERT photo record)
                       │
                       └─▶ SQS (Queue processing job)
                              │
                              ▼
                         Lambda (ProcessPhoto)
                              │
                              ├─▶ Textract (OCR)
                              │      │
                              │      └─▶ Extract blackboard text
                              │
                              ├─▶ Rekognition (Classify)
                              │      │
                              │      └─▶ Detect construction category
                              │
                              └─▶ RDS (UPDATE photo metadata)
```

---

## 3. フロントエンド設計

### 3.1 アーキテクチャパターン

**Next.js App Router + Server Components**

```
app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx                    # Server Component
│   └── layout.tsx
├── (dashboard)/
│   ├── layout.tsx                      # Shared layout
│   ├── page.tsx                        # Dashboard home
│   ├── upload/
│   │   └── page.tsx                    # Client Component (file upload)
│   ├── photos/
│   │   ├── page.tsx                    # Photo list (Server Component)
│   │   ├── [id]/
│   │   │   └── page.tsx                # Photo detail (SSR)
│   │   └── loading.tsx                 # Loading UI
│   ├── search/
│   │   └── page.tsx                    # Search (Client Component)
│   └── export/
│       └── page.tsx                    # Export wizard
├── api/
│   └── [...proxy]/
│       └── route.ts                    # API proxy to backend
└── layout.tsx                          # Root layout
```

### 3.2 状態管理

**Zustand + React Query**

```typescript
// store/photoStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Photo {
  id: string;
  fileName: string;
  url: string;
  category?: string;
  uploadProgress: number;
}

interface PhotoStore {
  photos: Photo[];
  uploadQueue: File[];
  addToQueue: (files: File[]) => void;
  uploadPhoto: (file: File) => Promise<void>;
  removeFromQueue: (index: number) => void;
  clearQueue: () => void;
}

export const usePhotoStore = create<PhotoStore>()(
  devtools(
    persist(
      (set, get) => ({
        photos: [],
        uploadQueue: [],

        addToQueue: (files) =>
          set((state) => ({
            uploadQueue: [...state.uploadQueue, ...files],
          })),

        uploadPhoto: async (file) => {
          const { uploadToS3 } = await import('@/lib/s3-upload');

          try {
            const url = await uploadToS3(file, (progress) => {
              // Update progress...
            });

            // Create metadata via API
            await fetch('/api/v1/photos', {
              method: 'POST',
              body: JSON.stringify({ fileName: file.name, url }),
            });

            set((state) => ({
              photos: [...state.photos, { id: crypto.randomUUID(), fileName: file.name, url, uploadProgress: 100 }],
            }));
          } catch (error) {
            console.error('Upload failed:', error);
            throw error;
          }
        },

        removeFromQueue: (index) =>
          set((state) => ({
            uploadQueue: state.uploadQueue.filter((_, i) => i !== index),
          })),

        clearQueue: () => set({ uploadQueue: [] }),
      }),
      { name: 'photo-store' }
    )
  )
);
```

**React Query for server state**

```typescript
// hooks/usePhotos.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function usePhotos(filters?: PhotoFilters) {
  return useQuery({
    queryKey: ['photos', filters],
    queryFn: () => apiClient.getPhotos(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function usePhotoDetail(id: string) {
  return useQuery({
    queryKey: ['photo', id],
    queryFn: () => apiClient.getPhoto(id),
    enabled: !!id,
  });
}

export function useUploadPhoto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => apiClient.uploadPhoto(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['photos'] });
    },
  });
}
```

### 3.3 主要コンポーネント設計

#### アップロードコンポーネント

```typescript
// components/upload/PhotoUploader.tsx
'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { usePhotoStore } from '@/store/photoStore';
import { Progress } from '@/components/ui/progress';

interface UploadProgress {
  [fileName: string]: number;
}

export function PhotoUploader() {
  const { addToQueue, uploadPhoto } = usePhotoStore();
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    addToQueue(acceptedFiles);
  }, [addToQueue]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tif', '.tiff'],
    },
    multiple: true,
  });

  const handleUploadAll = async () => {
    setIsUploading(true);
    const { uploadQueue } = usePhotoStore.getState();

    // 並列アップロード（最大10並列）
    const batchSize = 10;
    for (let i = 0; i < uploadQueue.length; i += batchSize) {
      const batch = uploadQueue.slice(i, i + batchSize);

      await Promise.all(
        batch.map((file) =>
          uploadPhoto(file).catch((err) => {
            console.error(`Failed to upload ${file.name}:`, err);
          })
        )
      );
    }

    setIsUploading(false);
  };

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        `}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <svg className="mx-auto h-12 w-12 text-gray-400" /* ... */ />
          <p className="text-lg font-medium">
            {isDragActive ? 'ここにドロップ' : 'ファイルをドラッグ&ドロップ'}
          </p>
          <p className="text-sm text-gray-500">または、クリックしてファイルを選択</p>
          <p className="text-xs text-gray-400">JPEG, TIFF形式（最大10,000枚）</p>
        </div>
      </div>

      {uploadQueue.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              {uploadQueue.length}枚のファイルが選択されています
            </p>
            <button
              onClick={handleUploadAll}
              disabled={isUploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isUploading ? 'アップロード中...' : 'アップロード開始'}
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto space-y-2">
            {uploadQueue.map((file, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded">
                <div className="flex-1">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {uploadProgress[file.name] !== undefined && (
                  <Progress value={uploadProgress[file.name]} className="w-32" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### 3.4 パフォーマンス最適化

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // 画像最適化
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.cloudfront.net',
      },
      {
        protocol: 'https',
        hostname: '*.s3.amazonaws.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Webpack最適化
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // クライアント側でのみ必要なモジュールを除外
      config.resolve.fallback = {
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },

  // 実験的機能
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
```

---

## 4. バックエンド設計

### 4.1 サービス構成

**ドメイン駆動設計（DDD）アプローチ**

```
backend/
├── api/                          # API Layer
│   ├── routes/
│   │   ├── photos.py            # Photo endpoints
│   │   ├── ai.py                # AI processing endpoints
│   │   └── export.py            # Export endpoints
│   └── middleware/
│       ├── auth.py              # Authentication
│       ├── validation.py        # Request validation
│       └── error_handler.py     # Error handling
├── domain/                       # Domain Layer
│   ├── models/
│   │   ├── photo.py             # Photo entity
│   │   ├── project.py           # Project entity
│   │   └── user.py              # User entity
│   ├── services/
│   │   ├── photo_service.py     # Business logic
│   │   ├── ocr_service.py       # OCR processing
│   │   └── classification_service.py
│   └── repositories/
│       ├── photo_repository.py  # Data access
│       └── project_repository.py
├── infrastructure/               # Infrastructure Layer
│   ├── aws/
│   │   ├── s3_client.py
│   │   ├── textract_client.py
│   │   └── rekognition_client.py
│   ├── database/
│   │   ├── connection.py
│   │   └── migrations/
│   └── cache/
│       └── redis_client.py
└── shared/                       # Shared utilities
    ├── config.py
    ├── logger.py
    └── exceptions.py
```

### 4.2 Lambda関数設計

#### 写真アップロード処理

```python
# lambda/photo_upload/handler.py
import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

BUCKET_NAME = os.environ['S3_BUCKET']
QUEUE_URL = os.environ['SQS_QUEUE_URL']
TABLE_NAME = os.environ['DYNAMODB_TABLE']

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    写真アップロードハンドラー

    Flow:
    1. S3 presigned URL生成
    2. DynamoDBにメタデータ保存
    3. SQSにOCR処理ジョブ送信
    """

    try:
        body = json.loads(event['body'])
        file_name = body['fileName']
        file_size = body['fileSize']
        content_type = body['contentType']

        # Presigned URL生成（15分有効）
        photo_id = generate_photo_id()
        s3_key = f"uploads/{photo_id}/{file_name}"

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=900
        )

        # DynamoDBに初期メタデータ保存
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                'photoId': photo_id,
                's3Key': s3_key,
                'fileName': file_name,
                'fileSize': file_size,
                'uploadDate': datetime.utcnow().isoformat(),
                'status': 'uploading',
                'processingStatus': 'pending'
            }
        )

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'photoId': photo_id,
                'uploadUrl': presigned_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def generate_photo_id() -> str:
    """ユニークな写真IDを生成"""
    import uuid
    return str(uuid.uuid4())
```

#### OCR処理（EventBridge トリガー）

```python
# lambda/ocr_processor/handler.py
import json
import boto3
from typing import Dict, Any
import re

textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['DYNAMODB_TABLE']

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    S3にアップロードされた画像のOCR処理

    EventBridge Rule:
    - S3 PutObject イベント
    - Prefix: uploads/
    """

    # S3イベントから情報取得
    s3_event = event['detail']
    bucket = s3_event['bucket']['name']
    key = s3_event['object']['key']

    # Textract実行
    response = textract_client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
    )

    # テキスト抽出
    extracted_text = extract_text_blocks(response)

    # 構造化データ抽出
    metadata = parse_blackboard_text(extracted_text)

    # DynamoDB更新
    photo_id = extract_photo_id_from_key(key)
    table = dynamodb.Table(TABLE_NAME)

    table.update_item(
        Key={'photoId': photo_id},
        UpdateExpression="""
            SET ocrText = :text,
                ocrMetadata = :metadata,
                processingStatus = :status,
                processedAt = :timestamp
        """,
        ExpressionAttributeValues={
            ':text': json.dumps(extracted_text, ensure_ascii=False),
            ':metadata': metadata,
            ':status': 'ocr_completed',
            ':timestamp': datetime.utcnow().isoformat()
        }
    )

    return {'statusCode': 200, 'body': json.dumps({'photoId': photo_id})}

def extract_text_blocks(response: Dict) -> list:
    """Textractレスポンスからテキストブロック抽出"""
    blocks = []
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            blocks.append({
                'text': block['Text'],
                'confidence': block['Confidence']
            })
    return blocks

def parse_blackboard_text(text_blocks: list) -> Dict:
    """黒板テキストから工事情報を抽出"""
    metadata = {
        '工事名': None,
        '工種': None,
        '測点': None,
        '撮影日': None
    }

    for block in text_blocks:
        text = block['text']

        # 測点パターン
        station_match = re.search(r'No\.?\s*(\d+[\+\-]?\d*\.?\d*)', text)
        if station_match:
            metadata['測点'] = f"No.{station_match.group(1)}"

        # 日付パターン
        date_match = re.search(r'(\d{4})[\-/](\d{1,2})[\-/](\d{1,2})', text)
        if date_match:
            metadata['撮影日'] = f"{date_match.group(1)}-{date_match.group(2):0>2}-{date_match.group(3):0>2}"

    return metadata
```

### 4.3 API Gateway設計

```yaml
# openapi.yaml (OpenAPI 3.0)
openapi: 3.0.0
info:
  title: Construction Photo Management API
  version: 1.0.0
  description: 工事写真管理システム API

servers:
  - url: https://api.photo-management.example.com/v1

paths:
  /photos:
    post:
      summary: 写真アップロード準備
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                fileName:
                  type: string
                  example: "IMG_0001.JPG"
                fileSize:
                  type: integer
                  example: 2048576
                contentType:
                  type: string
                  example: "image/jpeg"
      responses:
        '200':
          description: Presigned URL返却
          content:
            application/json:
              schema:
                type: object
                properties:
                  photoId:
                    type: string
                  uploadUrl:
                    type: string
      x-amazon-apigateway-integration:
        type: aws_proxy
        httpMethod: POST
        uri: arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-1:ACCOUNT_ID:function:photo-upload/invocations

    get:
      summary: 写真一覧取得
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 100
        - name: category
          in: query
          schema:
            type: string
      responses:
        '200':
          description: 写真一覧
          content:
            application/json:
              schema:
                type: object
                properties:
                  total:
                    type: integer
                  photos:
                    type: array
                    items:
                      $ref: '#/components/schemas/Photo'

components:
  schemas:
    Photo:
      type: object
      properties:
        id:
          type: string
        fileName:
          type: string
        uploadDate:
          type: string
          format: date-time
        category:
          type: string
        ocrText:
          type: string
        imageUrl:
          type: string
```

---

## 5. データベース設計

### 5.1 ER図

```
┌─────────────────┐         ┌─────────────────┐
│    projects     │         │      users      │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄───┐    │ id (PK)         │
│ name            │    │    │ email           │
│ contractor      │    │    │ name            │
│ start_date      │    │    │ role            │
│ end_date        │    │    │ created_at      │
│ status          │    │    └─────────────────┘
│ created_at      │    │
└─────────────────┘    │
                       │
                       │
┌─────────────────────┼──────────────────┐
│       photos        │                  │
├─────────────────────┤                  │
│ id (PK)             │                  │
│ project_id (FK)     ├──────────────────┘
│ user_id (FK)        │
│ file_name           │
│ s3_key              │
│ file_size           │
│ width               │
│ height              │
│ pixel_count         │
│ shooting_date       │
│ location            │  (POINT)
│ category            │
│ photo_type          │
│ work_type           │
│ work_kind           │
│ work_detail         │
│ title               │
│ ocr_text            │  (TEXT)
│ ocr_metadata        │  (JSONB)
│ classification_data │  (JSONB)
│ quality_score       │  (NUMERIC)
│ is_representative   │  (BOOLEAN)
│ perceptual_hash     │
│ processing_status   │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         │
         │
         ▼
┌─────────────────────┐
│  photo_duplicates   │
├─────────────────────┤
│ id (PK)             │
│ photo_id_1 (FK)     │
│ photo_id_2 (FK)     │
│ similarity_score    │
│ detected_at         │
└─────────────────────┘
```

### 5.2 テーブル定義（PostgreSQL）

```sql
-- プロジェクトテーブル
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    contractor VARCHAR(255),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);

-- ユーザーテーブル
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    cognito_sub VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- 写真テーブル
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),

    -- ファイル情報
    file_name VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL UNIQUE,
    file_size BIGINT NOT NULL,
    content_type VARCHAR(100),

    -- 画像メタデータ
    width INT,
    height INT,
    pixel_count INT,

    -- 撮影情報
    shooting_date DATE,
    location GEOGRAPHY(POINT, 4326),  -- PostGIS

    -- 分類情報
    category VARCHAR(100),
    photo_type VARCHAR(100),  -- 着手前及び完成写真、施工状況写真 等
    work_type VARCHAR(100),   -- 工種
    work_kind VARCHAR(100),   -- 種別
    work_detail VARCHAR(100), -- 細別
    title VARCHAR(255),

    -- OCRデータ
    ocr_text TEXT,
    ocr_metadata JSONB,
    ocr_confidence NUMERIC(5,2),

    -- AI分類データ
    classification_data JSONB,
    classification_confidence NUMERIC(5,2),

    -- 品質評価
    quality_score NUMERIC(5,2),
    sharpness_score NUMERIC(5,2),
    brightness_score NUMERIC(5,2),
    blackboard_readable BOOLEAN,

    -- 電子納品
    serial_number INT,
    is_representative BOOLEAN DEFAULT false,
    is_submission_frequency BOOLEAN DEFAULT false,

    -- 重複検出
    perceptual_hash VARCHAR(64),

    -- 処理ステータス
    processing_status VARCHAR(50) DEFAULT 'pending',

    -- タイムスタンプ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- インデックス
CREATE INDEX idx_photos_project ON photos(project_id);
CREATE INDEX idx_photos_category ON photos(category);
CREATE INDEX idx_photos_shooting_date ON photos(shooting_date);
CREATE INDEX idx_photos_processing_status ON photos(processing_status);
CREATE INDEX idx_photos_hash ON photos(perceptual_hash);
CREATE INDEX idx_photos_location ON photos USING GIST(location);  -- PostGIS

-- JSONB GIN インデックス
CREATE INDEX idx_photos_ocr_metadata ON photos USING GIN(ocr_metadata);
CREATE INDEX idx_photos_classification ON photos USING GIN(classification_data);

-- 全文検索インデックス
CREATE INDEX idx_photos_ocr_text_fts ON photos USING GIN(to_tsvector('japanese', ocr_text));

-- 重複写真テーブル
CREATE TABLE photo_duplicates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id_1 UUID REFERENCES photos(id) ON DELETE CASCADE,
    photo_id_2 UUID REFERENCES photos(id) ON DELETE CASCADE,
    similarity_score NUMERIC(5,2),
    hamming_distance INT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_duplicate_pair UNIQUE(photo_id_1, photo_id_2),
    CONSTRAINT check_different_photos CHECK (photo_id_1 != photo_id_2)
);

CREATE INDEX idx_duplicates_photo1 ON photo_duplicates(photo_id_1);
CREATE INDEX idx_duplicates_photo2 ON photo_duplicates(photo_id_2);

-- 更新日時自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_photos_updated_at BEFORE UPDATE ON photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.3 クエリパターン

#### 高速検索クエリ

```sql
-- 複合条件検索（位置+日付+カテゴリ+キーワード）
SELECT
    p.id,
    p.file_name,
    p.title,
    p.category,
    p.shooting_date,
    ST_AsText(p.location) as location_text,
    p.quality_score
FROM photos p
WHERE
    p.project_id = :project_id
    AND p.shooting_date BETWEEN :date_from AND :date_to
    AND p.category = :category
    AND ST_DWithin(
        p.location::geography,
        ST_MakePoint(:lng, :lat)::geography,
        :radius  -- meters
    )
    AND to_tsvector('japanese', p.ocr_text) @@ plainto_tsquery('japanese', :keyword)
ORDER BY p.shooting_date DESC
LIMIT 100;
```

#### 重複検出クエリ

```sql
-- パーセプチュアルハッシュによる類似写真検出
WITH target_photo AS (
    SELECT perceptual_hash FROM photos WHERE id = :target_id
)
SELECT
    p.id,
    p.file_name,
    p.perceptual_hash,
    -- ハミング距離計算（PostgreSQLのbit_count関数）
    bit_count(
        (p.perceptual_hash::bit(64) # (SELECT perceptual_hash::bit(64) FROM target_photo))
    ) as hamming_distance
FROM photos p
WHERE
    p.id != :target_id
    AND bit_count(
        (p.perceptual_hash::bit(64) # (SELECT perceptual_hash::bit(64) FROM target_photo))
    ) <= 5  -- 閾値
ORDER BY hamming_distance
LIMIT 20;
```

---

## 6. AI/ML基盤設計

### 6.1 AI処理パイプライン

```
写真アップロード
    │
    ▼
┌─────────────────┐
│  S3 Event       │
│  Notification   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ EventBridge     │
│ Rule            │
└────────┬────────┘
         │
         ├──▶ Lambda (OCR処理)
         │        │
         │        └──▶ Textract
         │               │
         │               └──▶ DynamoDB (OCR結果保存)
         │
         ├──▶ Lambda (画像分類)
         │        │
         │        └──▶ Rekognition Custom Labels
         │               │
         │               └──▶ DynamoDB (分類結果保存)
         │
         └──▶ Lambda (品質評価)
                  │
                  └──▶ カスタムモデル (SageMaker Endpoint)
                         │
                         └──▶ DynamoDB (品質スコア保存)
```

### 6.2 Amazon Textract設定

```python
# infrastructure/aws/textract_client.py
import boto3
from typing import Dict, List
from botocore.exceptions import ClientError

class TextractClient:
    def __init__(self):
        self.client = boto3.client('textract', region_name='ap-northeast-1')

    def analyze_document(self, s3_bucket: str, s3_key: str) -> Dict:
        """
        文書解析（テーブル、フォーム検出含む）

        料金:
        - $1.50 per 1,000 pages (detect_document_text)
        - $50 per 1,000 pages (analyze_document)
        """
        try:
            response = self.client.analyze_document(
                Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
                FeatureTypes=['TABLES', 'FORMS']
            )
            return self._parse_response(response)
        except ClientError as e:
            print(f"Textract error: {e}")
            raise

    def detect_text(self, s3_bucket: str, s3_key: str) -> List[Dict]:
        """
        テキスト検出（シンプル・低コスト）
        """
        response = self.client.detect_document_text(
            Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
        )

        lines = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                lines.append({
                    'text': block['Text'],
                    'confidence': block['Confidence'],
                    'geometry': block['Geometry']
                })

        return lines
```

### 6.3 Amazon Rekognition Custom Labels

```python
# infrastructure/aws/rekognition_client.py
import boto3

class RekognitionClient:
    def __init__(self):
        self.client = boto3.client('rekognition', region_name='ap-northeast-1')
        self.project_arn = 'arn:aws:rekognition:ap-northeast-1:ACCOUNT_ID:project/construction-classifier'
        self.model_arn = f'{self.project_arn}/version/production/1'

    def classify_photo(self, s3_bucket: str, s3_key: str) -> Dict:
        """
        カスタムラベル検出

        料金:
        - Training: $1.00/hour
        - Inference: $4.00/hour (running time) + $0.001/image
        """
        try:
            response = self.client.detect_custom_labels(
                ProjectVersionArn=self.model_arn,
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
                MinConfidence=70
            )

            labels = []
            for label in response['CustomLabels']:
                labels.append({
                    'name': label['Name'],
                    'confidence': label['Confidence']
                })

            return {
                'labels': labels,
                'primary_label': labels[0] if labels else None
            }
        except Exception as e:
            print(f"Classification error: {e}")
            return {'labels': [], 'primary_label': None}
```

### 6.4 カスタムモデル（品質評価）

```python
# ai-models/quality/model.py
import tensorflow as tf
from tensorflow import keras
import numpy as np

class PhotoQualityModel:
    """
    工事写真品質評価モデル

    評価項目:
    - シャープネス
    - 明るさ
    - 黒板判読性
    - 対象物の明瞭度
    """

    def __init__(self, model_path: str):
        self.model = keras.models.load_model(model_path)

    def predict(self, image_path: str) -> Dict:
        """品質スコア予測"""

        # 画像前処理
        img = keras.preprocessing.image.load_img(
            image_path,
            target_size=(224, 224)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, 0) / 255.0

        # 推論
        prediction = self.model.predict(img_array)[0]

        return {
            'overall_score': float(prediction[0] * 100),
            'sharpness_score': float(prediction[1] * 100),
            'brightness_score': float(prediction[2] * 100),
            'blackboard_readable': bool(prediction[3] > 0.5),
            'recommendation': self._get_recommendation(prediction[0])
        }

    def _get_recommendation(self, score: float) -> str:
        """推奨アクション"""
        if score >= 0.8:
            return "提出に最適"
        elif score >= 0.6:
            return "提出可能"
        elif score >= 0.4:
            return "要確認"
        else:
            return "再撮影推奨"
```

---

（続く: セクション7-10は次のレスポンスで提供）
