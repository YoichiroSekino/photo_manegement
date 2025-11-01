# 工事写真自動整理システム 開発計画書

**バージョン**: 1.0
**作成日**: 2025-11-02
**対象期間**: 6-12ヶ月
**開発体制**: 少人数チーム (1-3名)

---

## 目次

1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)
2. [プロジェクト概要](#2-プロジェクト概要)
3. [開発体制](#3-開発体制)
4. [開発スケジュール](#4-開発スケジュール)
5. [Phase 1: MVP開発 (Month 1-3)](#5-phase-1-mvp開発-month-1-3)
6. [Phase 2: AI強化 (Month 4-6)](#6-phase-2-ai強化-month-4-6)
7. [Phase 3: 電子納品対応 (Month 7-9)](#7-phase-3-電子納品対応-month-7-9)
8. [Phase 4: 連携・拡張 (Month 10-12)](#8-phase-4-連携拡張-month-10-12)
9. [品質保証計画](#9-品質保証計画)
10. [成果物](#10-成果物)

---

## 1. エグゼクティブサマリー

### 1.1 プロジェクトの目的

建設現場で撮影される大量の工事写真（最大20万枚）を、AIで自動的に整理・分類し、国土交通省「デジタル写真管理情報基準（令和5年3月版）」に完全準拠した形で管理するシステムを開発します。

### 1.2 主要な価値提供

- **工数削減**: 従来の手作業による写真整理作業を90%以上削減
- **基準準拠**: 国交省基準への完全準拠により、電子納品の確実性を保証
- **品質向上**: AI による重複・不良写真の自動検出で提出品質を向上
- **検索効率化**: 位置・日時・工種から瞬時に検索、必要な写真を即座に特定

### 1.3 開発期間とコスト概算

- **開発期間**: 6-12ヶ月（4フェーズ）
- **開発コスト**: 約1,500万円〜2,500万円
- **月間運用コスト**: 約10万円〜50万円（利用規模により変動）

---

## 2. プロジェクト概要

### 2.1 背景と課題

建設業界における工事写真管理の現状：

1. **大量の写真**: 1つの工事で数万〜20万枚の写真を撮影
2. **手作業の限界**: 分類・整理に膨大な時間（数百時間）が必要
3. **基準準拠の難しさ**: 国交省基準の複雑な命名規則・メタデータ要件
4. **検索困難**: 必要な写真を探すのに時間がかかる
5. **品質ばらつき**: 重複や不鮮明な写真が混在

### 2.2 ソリューション概要

本システムは以下の機能で課題を解決します：

| 機能領域 | 解決策 |
|---------|--------|
| **写真取込** | ドラッグ&ドロップで最大1万枚同時アップロード |
| **自動分類** | AI画像認識 + OCRで工種・写真区分を自動判定 |
| **品質管理** | 重複検出、画素数チェック、黒板判読性評価 |
| **検索** | 位置・日時・キーワード・工種による高速検索 |
| **電子納品** | PHOTO.XML自動生成（PHOTO05.DTD準拠） |
| **写真帳作成** | PDF/Excel形式の工事写真帳を自動生成 |

### 2.3 技術的な特徴

- **クラウドネイティブ**: AWS サーバーレスアーキテクチャで無限スケール
- **AI/ML活用**: Amazon Rekognition/Textract + カスタムモデル
- **高速処理**: 並列処理により1枚2秒以下で処理完了
- **Progressive Web App**: デスクトップ・モバイル両対応

### 2.4 対象ユーザー

- **一次ユーザー**: 建設会社の現場監督・工事写真担当者
- **二次ユーザー**: 発注者（国土交通省、地方自治体）
- **管理者**: システム管理者、親会社のIT部門

---

## 3. 開発体制

### 3.1 少人数チーム構成（1-3名想定）

#### パターンA: 1名体制（フルスタックエンジニア）

```
開発者A (フルスタック)
├── フロントエンド開発 (Next.js/TypeScript)
├── バックエンド開発 (Node.js/Python)
├── AI/ML実装 (AWS Rekognition/Textract設定)
├── インフラ構築 (AWS構成)
└── テスト・デプロイ
```

**推奨スキルセット**:
- React/Next.js, TypeScript
- Node.js または Python (FastAPI)
- AWS (Lambda, S3, RDS, Rekognition)
- 基本的なML知識

**開発期間**: 10-12ヶ月

#### パターンB: 2名体制（フロント/バック分担）

```
開発者A (フロントエンド + UI/UX)
├── Next.js/React開発
├── UI/UXデザイン
├── 地図表示 (Google Maps API)
└── ユーザーテスト

開発者B (バックエンド + AI/インフラ)
├── API開発 (Node.js/FastAPI)
├── AI/ML実装
├── データベース設計
└── AWS インフラ構築
```

**開発期間**: 8-10ヶ月

#### パターンC: 3名体制（専門分担）

```
開発者A (フロントエンド)
└── UI/UX, React/Next.js

開発者B (バックエンド)
└── API, データベース, ビジネスロジック

開発者C (AI/ML + DevOps)
└── AI実装, インフラ, CI/CD
```

**開発期間**: 6-8ヶ月

### 3.2 役割と責任範囲

| 役割 | 主な責任 | 週あたり工数 |
|------|---------|-------------|
| **フロントエンド開発** | UI実装、ユーザー体験最適化 | 30-40時間 |
| **バックエンド開発** | API設計、ビジネスロジック実装 | 30-40時間 |
| **AI/ML開発** | OCR、画像分類、モデル最適化 | 20-30時間 |
| **DevOps/インフラ** | AWS構築、CI/CD、監視設定 | 10-20時間 |
| **テスト** | 単体・結合・E2Eテスト作成 | 15-25時間 |
| **プロジェクト管理** | スケジュール管理、課題管理 | 5-10時間 |

### 3.3 開発環境

#### 必要なツール・サービス

```bash
# 開発環境
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git / GitHub

# IDEとツール
- VS Code + 拡張機能
  - ESLint, Prettier
  - AWS Toolkit
  - Python, Pylance
- Postman (API テスト)
- DBeaver (DB 管理)

# AWS アカウント
- 開発環境用アカウント
- 本番環境用アカウント (推奨)

# 外部サービス
- Google Maps API キー
- (オプション) Sentry (エラー監視)
- (オプション) GitHub Copilot
```

### 3.4 コミュニケーション

- **日次**: 進捗共有（Slack/Teams）
- **週次**: レビューミーティング（1時間）
- **隔週**: デモ・ユーザーフィードバック
- **ドキュメント**: GitHub Wiki/Notion

---

## 4. 開発スケジュール

### 4.1 全体タイムライン（標準：9ヶ月）

```
Month 1-3  : Phase 1 - MVP開発
Month 4-6  : Phase 2 - AI強化
Month 7-9  : Phase 3 - 電子納品対応
Month 10-12: Phase 4 - 連携・拡張 (オプション)
```

### 4.2 マイルストーン

| マイルストーン | 期限 | 成果物 |
|--------------|------|--------|
| **M1: プロジェクト開始** | Week 1 | 環境構築完了、技術検証完了 |
| **M2: MVP Alpha** | Month 2 | 基本アップロード・表示機能 |
| **M3: MVP Beta** | Month 3 | OCR統合、基本検索機能 |
| **M4: AI統合完了** | Month 6 | 自動分類、品質判定機能 |
| **M5: 電子納品対応** | Month 9 | PHOTO.XML生成、写真帳作成 |
| **M6: 本番リリース** | Month 9-12 | 運用開始 |

### 4.3 フェーズごとの目標

| Phase | 期間 | 主要目標 | 成功指標 |
|-------|------|---------|---------|
| **Phase 1** | 1-3ヶ月 | 基本機能実装 | 100枚の写真を正常にアップロード・表示 |
| **Phase 2** | 4-6ヶ月 | AI機能実装 | OCR精度85%以上、分類精度80%以上 |
| **Phase 3** | 7-9ヶ月 | 電子納品対応 | 国交省基準準拠のXML生成成功率100% |
| **Phase 4** | 10-12ヶ月 | 拡張機能 | 外部システム連携成功 |

---

## 5. Phase 1: MVP開発 (Month 1-3)

### 5.1 目標

最小限の機能で動作するプロトタイプを開発し、コアワークフローを検証します。

**成果物**:
- 写真アップロード機能
- 写真一覧表示
- 基本的な検索機能
- 黒板OCR（Amazon Textract統合）

### 5.2 Week 1-2: 環境構築・技術検証

#### タスク詳細

**Week 1: プロジェクトセットアップ**

```bash
# 1. リポジトリ作成
git init
git remote add origin <repository-url>

# 2. Next.js プロジェクト作成
npx create-next-app@latest frontend --typescript --app --tailwind
cd frontend
npm install

# 3. バックエンドセットアップ (FastAPI例)
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn boto3 psycopg2-binary pillow

# 4. Docker環境構築
# docker-compose.yml作成（PostgreSQL, Redis）
docker-compose up -d
```

**Week 2: AWS環境構築**

```bash
# AWS CLI設定
aws configure

# S3バケット作成
aws s3 mb s3://construction-photos-dev

# Lambda関数デプロイ準備
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# RDS PostgreSQL作成（開発環境）
# Terraform または AWS Console
```

#### 技術検証項目

1. **S3マルチパートアップロード検証**
   ```typescript
   // 1,000枚の写真を並列アップロードできるか？
   // 目標: 1枚あたり5秒以内
   ```

2. **Amazon Textract OCR精度検証**
   ```python
   # サンプル黒板画像で精度測定
   # 目標: 80%以上の文字認識精度
   ```

3. **PostgreSQL パフォーマンス検証**
   ```sql
   -- 10万件のメタデータで検索速度測定
   -- 目標: <500ms
   ```

### 5.3 Week 3-4: フロントエンド基盤

#### 実装内容

**1. プロジェクト構造**

```
frontend/
├── app/
│   ├── (auth)/
│   │   └── login/
│   ├── dashboard/
│   │   ├── page.tsx          # ダッシュボード
│   │   └── layout.tsx
│   ├── upload/
│   │   └── page.tsx          # アップロード画面
│   ├── photos/
│   │   ├── page.tsx          # 写真一覧
│   │   └── [id]/
│   │       └── page.tsx      # 写真詳細
│   └── search/
│       └── page.tsx          # 検索画面
├── components/
│   ├── ui/                   # shadcn/ui コンポーネント
│   ├── upload/
│   │   ├── DragDropZone.tsx
│   │   ├── UploadProgress.tsx
│   │   └── FileValidator.tsx
│   ├── photos/
│   │   ├── PhotoGrid.tsx
│   │   ├── PhotoCard.tsx
│   │   └── PhotoDetail.tsx
│   └── search/
│       ├── SearchBar.tsx
│       └── FilterPanel.tsx
├── lib/
│   ├── api.ts               # API クライアント
│   ├── s3-upload.ts         # S3アップロードロジック
│   └── validators.ts        # バリデーション
└── types/
    └── photo.ts             # TypeScript型定義
```

**2. 主要コンポーネント実装**

```typescript
// components/upload/DragDropZone.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface DragDropZoneProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
}

export function DragDropZone({ onFilesSelected, maxFiles = 10000 }: DragDropZoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // ファイルバリデーション
    const validFiles = acceptedFiles.filter(file => {
      const isImage = file.type.startsWith('image/');
      const isValidSize = file.size >= 100_000 && file.size <= 10_000_000; // 100KB-10MB
      return isImage && isValidSize;
    });

    onFilesSelected(validFiles);
  }, [onFilesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tif', '.tiff'],
    },
    maxFiles,
  });

  return (
    <div
      {...getRootProps()}
      className="border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
                 hover:border-blue-500 transition-colors"
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>ここにファイルをドロップ...</p>
      ) : (
        <div>
          <p>ファイルをドラッグ&ドロップ、またはクリックして選択</p>
          <p className="text-sm text-gray-500 mt-2">
            最大{maxFiles.toLocaleString()}枚まで同時アップロード可能
          </p>
        </div>
      )}
    </div>
  );
}
```

**3. S3アップロード実装**

```typescript
// lib/s3-upload.ts
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export class PhotoUploader {
  private s3Client: S3Client;

  constructor() {
    this.s3Client = new S3Client({
      region: process.env.NEXT_PUBLIC_AWS_REGION!,
      credentials: {
        accessKeyId: process.env.NEXT_PUBLIC_AWS_ACCESS_KEY_ID!,
        secretAccessKey: process.env.NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY!,
      },
    });
  }

  async uploadFile(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<string> {
    const fileName = `uploads/${Date.now()}_${file.name}`;

    try {
      const command = new PutObjectCommand({
        Bucket: process.env.NEXT_PUBLIC_S3_BUCKET!,
        Key: fileName,
        Body: file,
        ContentType: file.type,
      });

      await this.s3Client.send(command);

      return fileName;
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  }

  async uploadBatch(
    files: File[],
    onProgress?: (fileIndex: number, progress: UploadProgress) => void
  ): Promise<string[]> {
    // 並列アップロード（最大10並列）
    const batchSize = 10;
    const results: string[] = [];

    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize);
      const uploads = batch.map((file, index) =>
        this.uploadFile(file, (progress) => {
          onProgress?.(i + index, progress);
        })
      );

      const batchResults = await Promise.all(uploads);
      results.push(...batchResults);
    }

    return results;
  }
}
```

### 5.4 Week 5-6: バックエンドAPI

#### API設計

**RESTful エンドポイント**

```
POST   /api/v1/photos/upload              # 写真アップロード
GET    /api/v1/photos                     # 写真一覧取得
GET    /api/v1/photos/:id                 # 写真詳細取得
GET    /api/v1/photos/search              # 写真検索
POST   /api/v1/photos/:id/process         # OCR処理トリガー
GET    /api/v1/photos/:id/metadata        # メタデータ取得
PATCH  /api/v1/photos/:id/metadata        # メタデータ更新
```

**実装例（FastAPI）**

```python
# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import boto3
from datetime import datetime
import uuid

app = FastAPI(title="Construction Photo Management API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 開発環境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS クライアント
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
rekognition_client = boto3.client('rekognition')

# データベース接続
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/photo_management"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# モデル定義
from pydantic import BaseModel

class PhotoMetadata(BaseModel):
    id: str
    file_name: str
    s3_key: str
    upload_date: datetime
    file_size: int
    width: int
    height: int
    pixel_count: int
    shooting_date: Optional[str] = None
    location: Optional[dict] = None
    ocr_text: Optional[str] = None
    category: Optional[str] = None
    processing_status: str = "pending"

# エンドポイント実装
@app.post("/api/v1/photos/upload")
async def upload_photo(file: UploadFile = File(...)):
    """写真アップロード"""

    # ファイルバリデーション
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="画像ファイルのみアップロード可能です")

    # S3にアップロード
    photo_id = str(uuid.uuid4())
    s3_key = f"photos/{photo_id}/{file.filename}"

    try:
        s3_client.upload_fileobj(
            file.file,
            "construction-photos",
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アップロード失敗: {str(e)}")

    # メタデータをDBに保存
    db = SessionLocal()
    photo = PhotoMetadata(
        id=photo_id,
        file_name=file.filename,
        s3_key=s3_key,
        upload_date=datetime.utcnow(),
        file_size=file.size,
        processing_status="uploaded"
    )
    # DB保存処理...

    # 非同期でOCR処理をキューに追加
    # SQS にメッセージ送信

    return {"id": photo_id, "status": "uploaded"}

@app.get("/api/v1/photos")
async def list_photos(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """写真一覧取得"""
    db = SessionLocal()

    # クエリ構築
    query = db.query(Photo)

    if category:
        query = query.filter(Photo.category == category)
    if date_from:
        query = query.filter(Photo.shooting_date >= date_from)
    if date_to:
        query = query.filter(Photo.shooting_date <= date_to)

    photos = query.offset(skip).limit(limit).all()

    return {"total": query.count(), "photos": photos}

@app.get("/api/v1/photos/{photo_id}")
async def get_photo(photo_id: str):
    """写真詳細取得"""
    db = SessionLocal()
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="写真が見つかりません")

    # S3から署名付きURLを生成
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'construction-photos', 'Key': photo.s3_key},
        ExpiresIn=3600
    )

    return {
        **photo.__dict__,
        "image_url": presigned_url
    }
```

### 5.5 Week 7-8: OCR統合

#### Amazon Textract統合

```python
# backend/app/services/ocr_service.py
import boto3
from typing import Dict, List

class OCRService:
    def __init__(self):
        self.textract = boto3.client('textract')

    def process_blackboard(self, s3_bucket: str, s3_key: str) -> Dict:
        """黒板OCR処理"""

        response = self.textract.detect_document_text(
            Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
        )

        # テキスト抽出
        extracted_text = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                extracted_text.append({
                    'text': block['Text'],
                    'confidence': block['Confidence']
                })

        # 構造化データ抽出
        metadata = self._parse_blackboard_text(extracted_text)

        return metadata

    def _parse_blackboard_text(self, text_blocks: List[Dict]) -> Dict:
        """黒板テキストから工事情報を抽出"""

        metadata = {
            '工事名': None,
            '工種': None,
            '測点': None,
            '撮影日': None,
            '立会者': None,
            '寸法': {}
        }

        for block in text_blocks:
            text = block['text']
            confidence = block['confidence']

            # パターンマッチング
            if '工事' in text:
                metadata['工事名'] = text
            elif '測点' in text or 'No.' in text:
                metadata['測点'] = self._extract_station_number(text)
            elif '設計' in text or '実測' in text:
                metadata['寸法'] = self._extract_dimensions(text)
            # ... その他のパターン

        return metadata

    def _extract_station_number(self, text: str) -> str:
        """測点番号を抽出"""
        import re
        match = re.search(r'No\.?\s*(\d+[\+\-]?\d*\.?\d*)', text)
        return match.group(1) if match else None

    def _extract_dimensions(self, text: str) -> Dict:
        """寸法情報を抽出"""
        import re
        dimensions = {}

        # 設計寸法
        design_match = re.search(r'設計[：:]\s*(\d+)\s*mm', text)
        if design_match:
            dimensions['設計'] = int(design_match.group(1))

        # 実測寸法
        actual_match = re.search(r'実測[：:]\s*(\d+)\s*mm', text)
        if actual_match:
            dimensions['実測'] = int(actual_match.group(1))

        return dimensions
```

### 5.6 Week 9-10: 基本検索機能

#### 検索API実装

```python
@app.get("/api/v1/photos/search")
async def search_photos(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[int] = None,  # meters
):
    """写真検索"""

    db = SessionLocal()
    query = db.query(Photo)

    # キーワード検索
    if keyword:
        query = query.filter(
            Photo.ocr_text.contains(keyword) |
            Photo.file_name.contains(keyword)
        )

    # カテゴリフィルタ
    if category:
        query = query.filter(Photo.category == category)

    # 日付範囲フィルタ
    if date_from:
        query = query.filter(Photo.shooting_date >= date_from)
    if date_to:
        query = query.filter(Photo.shooting_date <= date_to)

    # 位置検索（円形範囲）
    if lat and lng and radius:
        # PostGISを使用した地理空間検索
        query = query.filter(
            func.ST_DWithin(
                Photo.location,
                func.ST_MakePoint(lng, lat),
                radius
            )
        )

    results = query.all()
    return {"count": len(results), "photos": results}
```

### 5.7 Week 11-12: 統合テストとMVPリリース

#### テスト項目

```typescript
// frontend/__tests__/upload.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadPage } from '@/app/upload/page';

describe('写真アップロード', () => {
  test('ファイル選択後にアップロードボタンが有効になる', async () => {
    render(<UploadPage />);

    const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText('ファイル選択');

    await userEvent.upload(input, file);

    const uploadButton = screen.getByText('アップロード開始');
    expect(uploadButton).toBeEnabled();
  });

  test('100枚の写真を正常にアップロードできる', async () => {
    render(<UploadPage />);

    const files = Array.from({ length: 100 }, (_, i) =>
      new File([`photo${i}`], `photo${i}.jpg`, { type: 'image/jpeg' })
    );

    const input = screen.getByLabelText('ファイル選択');
    await userEvent.upload(input, files);

    const uploadButton = screen.getByText('アップロード開始');
    await userEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('100枚のアップロード完了')).toBeInTheDocument();
    }, { timeout: 60000 });
  });
});
```

#### パフォーマンステスト

```python
# backend/tests/performance_test.py
import asyncio
import time
from locust import HttpUser, task, between

class PhotoUploadUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_photo(self):
        """写真アップロードの負荷テスト"""
        files = {'file': ('test.jpg', open('test_data/sample.jpg', 'rb'), 'image/jpeg')}
        self.client.post("/api/v1/photos/upload", files=files)

    @task(3)
    def search_photos(self):
        """検索の負荷テスト"""
        self.client.get("/api/v1/photos/search?keyword=基礎工")

# 実行コマンド
# locust -f performance_test.py --host=http://localhost:8000
```

---

## 6. Phase 2: AI強化 (Month 4-6)

### 6.1 目標

AI/MLを活用した高度な自動分類・品質判定機能を実装します。

**成果物**:
- 画像認識による工種自動分類
- 重複写真検出
- 画質・品質自動判定
- 自動タイトル生成

### 6.2 Month 4: 画像分類モデル開発

#### Amazon Rekognition統合

```python
# backend/app/services/image_classification_service.py
import boto3
from typing import List, Dict

class ImageClassificationService:
    def __init__(self):
        self.rekognition = boto3.client('rekognition')

    def classify_construction_photo(self, s3_bucket: str, s3_key: str) -> Dict:
        """工事写真の分類"""

        # カスタムラベル検出
        response = self.rekognition.detect_custom_labels(
            ProjectVersionArn='arn:aws:rekognition:ap-northeast-1:xxx:project/construction-classifier/version/1',
            Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
            MinConfidence=70
        )

        classifications = []
        for label in response['CustomLabels']:
            classifications.append({
                'category': label['Name'],
                'confidence': label['Confidence']
            })

        # 最も確信度の高いカテゴリを返す
        if classifications:
            best_match = max(classifications, key=lambda x: x['confidence'])
            return {
                'category': best_match['category'],
                'confidence': best_match['confidence'],
                'all_predictions': classifications
            }

        return {'category': 'その他', 'confidence': 0}

    def detect_objects(self, s3_bucket: str, s3_key: str) -> List[Dict]:
        """物体検出（機材、設備等）"""

        response = self.rekognition.detect_labels(
            Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
            MaxLabels=10,
            MinConfidence=80
        )

        objects = []
        for label in response['Labels']:
            objects.append({
                'name': label['Name'],
                'confidence': label['Confidence'],
                'instances': len(label.get('Instances', []))
            })

        return objects
```

#### カスタムモデル学習（オプション）

```python
# ai-models/classification/train_model.py
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

class ConstructionPhotoClassifier:
    """工事写真分類モデル"""

    CATEGORIES = [
        "着手前及び完成写真",
        "施工状況写真",
        "安全管理写真",
        "使用材料写真",
        "品質管理写真",
        "出来形管理写真",
        "災害写真",
        "その他"
    ]

    def __init__(self):
        self.model = self._build_model()

    def _build_model(self):
        """モデル構築（転移学習）"""

        base_model = keras.applications.ResNet50V2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        base_model.trainable = False

        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.CATEGORIES), activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def train(self, train_data_path: str, epochs: int = 20):
        """モデル学習"""

        # データ拡張
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )

        train_generator = datagen.flow_from_directory(
            train_data_path,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training'
        )

        val_generator = datagen.flow_from_directory(
            train_data_path,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='validation'
        )

        # 学習
        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=val_generator
        )

        return history

    def predict(self, image_path: str) -> Dict:
        """推論"""

        img = keras.preprocessing.image.load_img(
            image_path,
            target_size=(224, 224)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, 0) / 255.0

        predictions = self.model.predict(img_array)[0]

        results = []
        for i, category in enumerate(self.CATEGORIES):
            results.append({
                'category': category,
                'probability': float(predictions[i])
            })

        results.sort(key=lambda x: x['probability'], reverse=True)

        return {
            'top_category': results[0]['category'],
            'confidence': results[0]['probability'],
            'all_predictions': results
        }
```

### 6.3 Month 5: 重複検出・品質判定

#### 重複検出（パーセプチュアルハッシュ）

```python
# backend/app/services/duplicate_detection_service.py
import imagehash
from PIL import Image
from typing import List, Tuple

class DuplicateDetectionService:
    def __init__(self, threshold: int = 5):
        self.threshold = threshold  # ハミング距離の閾値

    def calculate_hash(self, image_path: str) -> str:
        """画像のパーセプチュアルハッシュを計算"""
        img = Image.open(image_path)
        return str(imagehash.phash(img))

    def find_duplicates(self, photo_hashes: List[Tuple[str, str]]) -> List[List[str]]:
        """
        重複写真を検出

        Args:
            photo_hashes: [(photo_id, hash_value), ...]

        Returns:
            重複グループのリスト [[id1, id2], [id3, id4, id5], ...]
        """
        duplicates = []
        processed = set()

        for i, (id1, hash1) in enumerate(photo_hashes):
            if id1 in processed:
                continue

            group = [id1]
            hash1_obj = imagehash.hex_to_hash(hash1)

            for j, (id2, hash2) in enumerate(photo_hashes[i+1:], start=i+1):
                if id2 in processed:
                    continue

                hash2_obj = imagehash.hex_to_hash(hash2)
                distance = hash1_obj - hash2_obj

                if distance <= self.threshold:
                    group.append(id2)
                    processed.add(id2)

            if len(group) > 1:
                duplicates.append(group)
                processed.add(id1)

        return duplicates
```

#### 品質判定

```python
# backend/app/services/quality_assessment_service.py
from PIL import Image
import cv2
import numpy as np

class QualityAssessmentService:
    def assess_photo_quality(self, image_path: str) -> Dict:
        """写真品質を総合評価"""

        # 画像読み込み
        img_pil = Image.open(image_path)
        img_cv = cv2.imread(image_path)

        # 各種評価
        pixel_check = self._check_pixel_count(img_pil)
        sharpness = self._calculate_sharpness(img_cv)
        brightness = self._calculate_brightness(img_cv)
        blackboard_readable = self._check_blackboard_readability(img_cv)

        # 総合スコア計算
        score = self._calculate_overall_score(
            pixel_check, sharpness, brightness, blackboard_readable
        )

        return {
            'overall_score': score,
            'pixel_count_valid': pixel_check['valid'],
            'pixel_count': pixel_check['count'],
            'sharpness_score': sharpness,
            'brightness_score': brightness,
            'blackboard_readable': blackboard_readable,
            'recommendation': self._get_recommendation(score)
        }

    def _check_pixel_count(self, img: Image.Image) -> Dict:
        """有効画素数チェック"""
        width, height = img.size
        pixel_count = width * height

        valid = 1_000_000 <= pixel_count <= 3_000_000
        recommended = 1_800_000 <= pixel_count <= 2_200_000

        return {
            'valid': valid,
            'recommended': recommended,
            'count': pixel_count,
            'dimensions': f"{width}x{height}"
        }

    def _calculate_sharpness(self, img: np.ndarray) -> float:
        """シャープネス計算（Laplacian分散）"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        # 0-100のスコアに正規化
        score = min(100, variance / 10)
        return round(score, 2)

    def _calculate_brightness(self, img: np.ndarray) -> float:
        """明るさ評価"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = hsv[:, :, 2].mean()

        # 最適範囲: 80-180
        if 80 <= brightness <= 180:
            score = 100
        elif brightness < 80:
            score = (brightness / 80) * 100
        else:
            score = ((255 - brightness) / 75) * 100

        return round(score, 2)

    def _check_blackboard_readability(self, img: np.ndarray) -> bool:
        """黒板文字の判読性チェック（簡易版）"""
        # エッジ検出で文字の有無を判定
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size

        # エッジ密度が一定以上なら文字ありと判定
        return edge_density > 0.05

    def _calculate_overall_score(
        self, pixel_check: Dict, sharpness: float,
        brightness: float, blackboard_readable: bool
    ) -> float:
        """総合スコア計算"""
        score = 0

        # 画素数（30点）
        if pixel_check['recommended']:
            score += 30
        elif pixel_check['valid']:
            score += 20

        # シャープネス（30点）
        score += (sharpness / 100) * 30

        # 明るさ（20点）
        score += (brightness / 100) * 20

        # 黒板判読性（20点）
        if blackboard_readable:
            score += 20

        return round(score, 2)

    def _get_recommendation(self, score: float) -> str:
        """推奨アクション"""
        if score >= 80:
            return "提出に最適"
        elif score >= 60:
            return "提出可能"
        elif score >= 40:
            return "要確認"
        else:
            return "再撮影推奨"
```

### 6.4 Month 6: 自動タイトル生成

```python
# backend/app/services/title_generation_service.py
from typing import Dict, Optional

class TitleGenerationService:
    def generate_title(
        self,
        ocr_data: Dict,
        classification: str,
        shooting_date: str
    ) -> str:
        """
        写真タイトルを自動生成

        フォーマット: [工種]_[測点]_[撮影対象]_[撮影日]
        例: "基礎工_No.15+20.5_配筋状況_20240315"
        """

        parts = []

        # 工種
        work_type = ocr_data.get('工種') or self._infer_work_type(classification)
        if work_type:
            parts.append(work_type)

        # 測点
        station = ocr_data.get('測点')
        if station:
            parts.append(station)

        # 撮影対象（分類から推定）
        subject = self._get_subject_from_classification(classification)
        parts.append(subject)

        # 撮影日（YYYYMMDD形式）
        date_str = shooting_date.replace('-', '')
        parts.append(date_str)

        return '_'.join(parts)

    def _infer_work_type(self, classification: str) -> Optional[str]:
        """分類から工種を推定"""
        work_type_map = {
            '施工状況写真': '土工',
            '品質管理写真': '基礎工',
            '出来形管理写真': '基礎工',
            # ... その他のマッピング
        }
        return work_type_map.get(classification)

    def _get_subject_from_classification(self, classification: str) -> str:
        """分類から撮影対象を取得"""
        subject_map = {
            '着手前及び完成写真': '全景',
            '施工状況写真': '施工状況',
            '安全管理写真': '安全設備',
            '使用材料写真': '材料',
            '品質管理写真': '品質確認',
            '出来形管理写真': '出来形',
            '災害写真': '災害状況',
            'その他': 'その他'
        }
        return subject_map.get(classification, 'その他')
```

---

## 7. Phase 3: 電子納品対応 (Month 7-9)

### 7.1 目標

国土交通省「デジタル写真管理情報基準」に完全準拠した電子納品機能を実装します。

**成果物**:
- PHOTO.XML自動生成（PHOTO05.DTD準拠）
- ファイル名自動リネーム（Pnnnnnnn.JPG形式）
- フォルダ構造自動生成
- 工事写真帳作成（PDF/Excel）

### 7.2 Month 7: PHOTO.XML生成

#### XMLジェネレーター実装

```python
# backend/app/services/photo_xml_generator.py
from xml.etree.ElementTree import Element, SubElement, ElementTree
import xml.dom.minidom as minidom

class PhotoXMLGenerator:
    """PHOTO05.DTD準拠のXML生成"""

    def __init__(self):
        self.dtd_version = "05"
        self.standard_code = "土木202303-01"

    def generate_xml(
        self,
        photos: List[Dict],
        project_info: Dict,
        output_path: str
    ) -> str:
        """PHOTO.XMLを生成"""

        # ルート要素
        root = Element('photodata', DTD_version=self.dtd_version)

        # 基礎情報
        basic_info = SubElement(root, '基礎情報')
        SubElement(basic_info, '写真フォルダ名').text = 'PHOTO/PIC'
        SubElement(basic_info, '参考図フォルダ名').text = 'PHOTO/DRA'
        SubElement(basic_info, '適用要領基準').text = self.standard_code

        # 各写真の情報
        for photo in photos:
            photo_info = SubElement(root, '写真情報')

            # 写真ファイル情報
            file_info = SubElement(photo_info, '写真ファイル情報')
            SubElement(file_info, 'シリアル番号').text = str(photo['serial_number'])
            SubElement(file_info, '写真ファイル名').text = photo['file_name']
            SubElement(file_info, '写真ファイル日本語名').text = photo['japanese_name']
            SubElement(file_info, 'メディア番号').text = str(photo['media_number'])

            # 撮影工種区分
            classification = SubElement(photo_info, '撮影工種区分')
            SubElement(classification, '写真-大分類').text = photo['major_category']
            SubElement(classification, '写真区分').text = photo['photo_type']

            if photo.get('work_type'):
                SubElement(classification, '工種').text = photo['work_type']
            if photo.get('work_kind'):
                SubElement(classification, '種別').text = photo['work_kind']
            if photo.get('work_detail'):
                SubElement(classification, '細別').text = photo['work_detail']

            SubElement(classification, '写真タイトル').text = photo['title']

            # 付加情報（オプション）
            if photo.get('reference_drawing'):
                additional = SubElement(photo_info, '付加情報')
                SubElement(additional, '参考図ファイル名').text = photo['reference_drawing']
                SubElement(additional, '参考図タイトル').text = photo.get('drawing_title', '')

            # 撮影情報
            shooting_info = SubElement(photo_info, '撮影情報')
            if photo.get('location'):
                SubElement(shooting_info, '撮影箇所').text = photo['location']
            SubElement(shooting_info, '撮影年月日').text = photo['shooting_date']

            # 代表写真・提出頻度写真フラグ
            SubElement(photo_info, '代表写真').text = '1' if photo.get('is_representative') else '0'
            SubElement(photo_info, '提出頻度写真').text = '1' if photo.get('is_submission_frequency') else '0'

            # 施工管理値（オプション）
            if photo.get('measurement'):
                SubElement(photo_info, '施工管理値').text = photo['measurement']

        # XML整形
        xml_str = self._prettify_xml(root)

        # ファイル保存（Shift_JIS エンコード）
        with open(output_path, 'w', encoding='shift_jis') as f:
            f.write('<?xml version="1.0" encoding="Shift_JIS"?>\n')
            f.write('<!DOCTYPE photodata SYSTEM "PHOTO05.DTD">\n')
            f.write('<?xml-stylesheet type="text/xsl" href="PHOTO05.XSL"?>\n')
            f.write(xml_str)

        return output_path

    def _prettify_xml(self, elem: Element) -> str:
        """XML整形"""
        rough_string = ElementTree.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")[23:]  # XML宣言を除去

    def validate_xml(self, xml_path: str) -> Dict:
        """XML検証"""
        errors = []
        warnings = []

        tree = ElementTree.parse(xml_path)
        root = tree.getroot()

        # 必須項目チェック
        required_fields = [
            '基礎情報/写真フォルダ名',
            '基礎情報/適用要領基準',
            '写真情報/写真ファイル情報/シリアル番号',
            '写真情報/写真ファイル情報/写真ファイル名',
            '写真情報/撮影工種区分/写真-大分類',
            '写真情報/撮影工種区分/写真タイトル',
            '写真情報/撮影情報/撮影年月日',
        ]

        for field in required_fields:
            if not root.find(field.replace('/', '//')):
                errors.append(f"必須項目が見つかりません: {field}")

        # 文字数制限チェック
        for photo_info in root.findall('.//写真情報'):
            title = photo_info.find('.//写真タイトル')
            if title is not None and len(title.text) > 127:
                warnings.append(f"写真タイトルが127文字を超えています: {title.text[:20]}...")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
```

### 7.3 Month 8: ファイル管理・エクスポート

#### ファイル名リネームとフォルダ構造生成

```python
# backend/app/services/export_service.py
import os
import shutil
from pathlib import Path
from typing import List, Dict

class ExportService:
    def __init__(self):
        self.xml_generator = PhotoXMLGenerator()

    def export_electronic_delivery(
        self,
        project_id: str,
        photo_ids: List[str],
        output_dir: str
    ) -> str:
        """電子納品パッケージを作成"""

        # ディレクトリ構造作成
        photo_dir = Path(output_dir) / 'PHOTO'
        pic_dir = photo_dir / 'PIC'
        dra_dir = photo_dir / 'DRA'

        pic_dir.mkdir(parents=True, exist_ok=True)
        dra_dir.mkdir(parents=True, exist_ok=True)

        # 写真データ取得
        db = SessionLocal()
        photos = db.query(Photo).filter(Photo.id.in_(photo_ids)).all()

        # ファイルコピー＆リネーム
        xml_photos = []
        for i, photo in enumerate(photos, start=1):
            # 新しいファイル名（Pnnnnnnn.JPG形式）
            new_filename = f"P{i:07d}.JPG"

            # S3からダウンロード
            s3_client.download_file(
                'construction-photos',
                photo.s3_key,
                str(pic_dir / new_filename)
            )

            # XML用データ作成
            xml_photos.append({
                'serial_number': i,
                'file_name': new_filename,
                'japanese_name': photo.original_filename,
                'media_number': 1,
                'major_category': '工事',
                'photo_type': photo.category,
                'work_type': photo.work_type,
                'title': photo.title,
                'shooting_date': photo.shooting_date,
                'location': photo.location_text,
                'is_representative': photo.is_representative,
                'is_submission_frequency': photo.is_submission_frequency,
                'measurement': photo.measurement
            })

        # PHOTO.XML生成
        project = db.query(Project).filter(Project.id == project_id).first()
        xml_path = photo_dir / 'PHOTO.XML'

        self.xml_generator.generate_xml(
            photos=xml_photos,
            project_info={
                'name': project.name,
                'contractor': project.contractor
            },
            output_path=str(xml_path)
        )

        # DTDファイルコピー
        shutil.copy('templates/PHOTO05.DTD', photo_dir / 'PHOTO05.DTD')
        shutil.copy('templates/PHOTO05.XSL', photo_dir / 'PHOTO05.XSL')

        # ZIPアーカイブ作成
        zip_path = f"{output_dir}/electronic_delivery_{project_id}.zip"
        shutil.make_archive(
            zip_path.replace('.zip', ''),
            'zip',
            output_dir,
            'PHOTO'
        )

        return zip_path
```

### 7.4 Month 9: 工事写真帳生成

#### PDF生成

```python
# backend/app/services/photo_album_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from PIL import Image

class PhotoAlbumGenerator:
    """工事写真帳PDF生成"""

    def __init__(self):
        self.page_width, self.page_height = A4

    def generate_album(
        self,
        photos: List[Dict],
        project_info: Dict,
        output_path: str,
        layout: str = 'standard'  # standard, compact, detailed
    ) -> str:
        """工事写真帳PDF生成"""

        c = canvas.Canvas(output_path, pagesize=A4)

        # 表紙
        self._draw_cover_page(c, project_info)
        c.showPage()

        # 写真ページ
        if layout == 'standard':
            # 1ページ2枚レイアウト
            for i in range(0, len(photos), 2):
                self._draw_standard_layout(c, photos[i:i+2])
                c.showPage()

        elif layout == 'compact':
            # 1ページ4枚レイアウト
            for i in range(0, len(photos), 4):
                self._draw_compact_layout(c, photos[i:i+4])
                c.showPage()

        c.save()
        return output_path

    def _draw_cover_page(self, c: canvas.Canvas, project_info: Dict):
        """表紙ページ"""
        c.setFont("HeiseiMin-W3", 24)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 100*mm,
            "工事写真帳"
        )

        c.setFont("HeiseiMin-W3", 14)
        y = self.page_height - 140*mm

        info_items = [
            f"工事名: {project_info['name']}",
            f"施工業者: {project_info['contractor']}",
            f"工期: {project_info['start_date']} 〜 {project_info['end_date']}",
            f"作成日: {project_info['created_date']}"
        ]

        for item in info_items:
            c.drawString(50*mm, y, item)
            y -= 10*mm

    def _draw_standard_layout(self, c: canvas.Canvas, photos: List[Dict]):
        """標準レイアウト（1ページ2枚）"""

        for i, photo in enumerate(photos):
            y_offset = 250*mm if i == 0 else 120*mm

            # 写真挿入
            img_path = f"/tmp/{photo['id']}.jpg"
            # S3からダウンロード...

            img = Image.open(img_path)
            img_width, img_height = img.size

            # アスペクト比を保持してリサイズ
            max_width = 150*mm
            max_height = 100*mm
            scale = min(max_width / img_width, max_height / img_height)

            c.drawImage(
                img_path,
                30*mm,
                y_offset - 100*mm,
                width=img_width * scale,
                height=img_height * scale
            )

            # タイトルと情報
            c.setFont("HeiseiMin-W3", 10)
            c.drawString(30*mm, y_offset - 110*mm, photo['title'])

            # メタデータテーブル
            data = [
                ['撮影日', photo['shooting_date']],
                ['撮影箇所', photo['location']],
                ['工種', photo['work_type']],
            ]

            table = Table(data, colWidths=[40*mm, 110*mm])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))

            table.wrapOn(c, 150*mm, 200*mm)
            table.drawOn(c, 30*mm, y_offset - 140*mm)
```

---

## 8. Phase 4: 連携・拡張 (Month 10-12)

### 8.1 目標

外部システム連携とエンタープライズ機能を実装します。

**成果物**:
- 施工管理ソフトウェア連携API
- モバイルアプリ対応（PWA）
- 高度な分析機能
- 管理者ダッシュボード

### 8.2 詳細計画

（Phase 4は オプション拡張フェーズのため、詳細は省略）

主要タスク:
- RESTful API拡張（Webhook対応）
- OAuth2.0認証実装
- モバイル最適化
- 利用統計・分析ダッシュボード

---

## 9. 品質保証計画

### 9.1 テスト戦略

| テストレベル | カバレッジ目標 | 実施タイミング |
|------------|--------------|--------------|
| **単体テスト** | 80%以上 | コミット前 |
| **結合テスト** | 主要フロー100% | 週次 |
| **E2Eテスト** | クリティカルパス100% | リリース前 |
| **パフォーマンステスト** | - | Phase 完了時 |
| **セキュリティテスト** | OWASP Top 10 | Phase 3完了時 |

### 9.2 コード品質管理

```bash
# 自動テスト実行
npm run test:unit          # 単体テスト
npm run test:integration   # 結合テスト
npm run test:e2e          # E2Eテスト

# コード品質チェック
npm run lint              # ESLint
npm run type-check        # TypeScript型チェック
npm run test:coverage     # カバレッジレポート
```

---

## 10. 成果物

### 10.1 Phase別成果物

| Phase | 成果物 | 形式 |
|-------|--------|------|
| **Phase 1** | MVPアプリケーション | デプロイ済みアプリ |
| | 技術ドキュメント | Markdown |
| | APIドキュメント | OpenAPI仕様書 |
| **Phase 2** | AI分類モデル | TensorFlow/PyTorch |
| | 品質評価システム | Python パッケージ |
| **Phase 3** | 電子納品機能 | 統合済みアプリ |
| | PHOTO.XML生成ツール | Python CLI |
| **Phase 4** | 連携API | RESTful API |
| | 運用マニュアル | PDF |

### 10.2 最終納品物

1. **ソースコード** (GitHub リポジトリ)
2. **AWSインフラ** (Terraform コード含む)
3. **技術ドキュメント一式**
4. **ユーザーマニュアル**
5. **運用手順書**
6. **テストレポート**

---

**本開発計画書は、プロジェクトの進行に応じて適宜更新されます。**
