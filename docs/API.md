# 工事写真自動整理システム API ドキュメント

**バージョン**: 0.2.0 (Phase 2 - AI機能強化)
**最終更新**: 2025-11-02

---

## 目次

1. [概要](#概要)
2. [認証](#認証)
3. [エンドポイント一覧](#エンドポイント一覧)
4. [写真管理API](#写真管理api)
5. [OCR処理API](#ocr処理api)
6. [画像分類API](#画像分類api)
7. [検索API](#検索api)
8. [エラーレスポンス](#エラーレスポンス)
9. [データモデル](#データモデル)

---

## 概要

### ベースURL

```
http://localhost:8000/api/v1
```

### レスポンス形式

全てのレスポンスはJSON形式です。

### HTTPステータスコード

| コード | 意味 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 400 | リクエストエラー |
| 404 | リソースが見つからない |
| 422 | バリデーションエラー |
| 500 | サーバーエラー |

---

## 認証

Phase 1 MVPでは認証は実装されていません。Phase 2で実装予定です。

---

## エンドポイント一覧

### 写真管理

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| POST | `/photos` | 写真を作成 |
| GET | `/photos` | 写真一覧を取得 |
| GET | `/photos/{id}` | 写真詳細を取得 |

### OCR処理

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| POST | `/photos/{id}/process-ocr` | OCR処理を実行 |
| GET | `/photos/{id}/ocr-result` | OCR結果を取得 |

### 画像分類（Rekognition）

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| POST | `/photos/{id}/classify` | 画像分類を実行 |
| GET | `/photos/{id}/classification` | 分類結果を取得 |

### 検索

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/photos/search` | 写真を検索 |

---

## 写真管理API

### 写真を作成

写真メタデータをデータベースに登録します。

**エンドポイント**: `POST /api/v1/photos`

**リクエストボディ**:

```json
{
  "file_name": "P0000001.jpg",
  "file_size": 2048000,
  "mime_type": "image/jpeg",
  "s3_key": "photos/2024/03/P0000001.jpg",
  "title": "基礎配筋検査",
  "description": "基礎配筋の検査状況",
  "shooting_date": "2024-03-15T14:30:00",
  "work_type": "基礎工",
  "work_kind": "配筋工",
  "latitude": "35.6762",
  "longitude": "139.6503",
  "tags": ["検査", "配筋"]
}
```

**レスポンス**: `201 Created`

```json
{
  "id": 1,
  "file_name": "P0000001.jpg",
  "file_size": 2048000,
  "mime_type": "image/jpeg",
  "s3_key": "photos/2024/03/P0000001.jpg",
  "s3_url": null,
  "thumbnail_url": null,
  "title": "基礎配筋検査",
  "description": "基礎配筋の検査状況",
  "shooting_date": "2024-03-15T14:30:00",
  "latitude": "35.6762",
  "longitude": "139.6503",
  "location_address": null,
  "tags": ["検査", "配筋"],
  "major_category": null,
  "photo_type": null,
  "work_type": "基礎工",
  "work_kind": "配筋工",
  "work_detail": null,
  "metadata": null,
  "is_processed": false,
  "is_representative": false,
  "is_submission_frequency": false,
  "created_at": "2024-11-02T12:34:56.789012",
  "updated_at": "2024-11-02T12:34:56.789012"
}
```

### 写真一覧を取得

登録されている写真の一覧を取得します（ページネーション対応）。

**エンドポイント**: `GET /api/v1/photos`

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| page | integer | 1 | ページ番号 |
| page_size | integer | 20 | 1ページあたりの件数 |

**レスポンス**: `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "file_name": "P0000001.jpg",
      "title": "基礎配筋検査",
      ...
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 写真詳細を取得

指定されたIDの写真詳細を取得します。

**エンドポイント**: `GET /api/v1/photos/{id}`

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| id | integer | 写真ID |

**レスポンス**: `200 OK`

```json
{
  "id": 1,
  "file_name": "P0000001.jpg",
  "file_size": 2048000,
  ...
}
```

**エラーレスポンス**: `404 Not Found`

```json
{
  "detail": "写真が見つかりません（ID: 999）"
}
```

---

## OCR処理API

### OCR処理を実行

写真に対してAmazon Textractを使用したOCR処理を実行し、黒板情報を抽出します。

**エンドポイント**: `POST /api/v1/photos/{id}/process-ocr`

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| id | integer | 写真ID |

**レスポンス**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "completed",
  "blackboard_data": {
    "work_name": "○○○○工事",
    "work_type": "土工",
    "work_kind": "掘削工",
    "station": "100+5.0",
    "shooting_date": "2024-03-15",
    "design_dimension": 500,
    "actual_dimension": 498,
    "inspector": "山田太郎"
  }
}
```

### OCR結果を取得

写真のOCR処理結果を取得します。

**エンドポイント**: `GET /api/v1/photos/{id}/ocr-result`

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| id | integer | 写真ID |

**レスポンス（処理済み）**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "completed",
  "work_name": "○○○○工事",
  "work_type": "土工",
  "work_kind": "掘削工",
  "station": "100+5.0",
  "shooting_date": "2024-03-15",
  "design_dimension": 500,
  "actual_dimension": 498,
  "inspector": "山田太郎"
}
```

**レスポンス（未処理）**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "not_processed",
  "work_name": null,
  "work_type": null,
  ...
}
```

---

## 画像分類API

### 画像分類を実行

Amazon Rekognitionを使用して写真から物体・シーン・作業員・安全装備などを検出します。

**エンドポイント**: `POST /api/v1/photos/{id}/classify`

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| id | integer | 写真ID |

**レスポンス**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "completed",
  "labels": [
    {
      "name": "Construction",
      "confidence": 95.5,
      "parents": []
    },
    {
      "name": "Excavator",
      "confidence": 92.3,
      "parents": []
    },
    {
      "name": "Worker",
      "confidence": 88.7,
      "parents": ["Person"]
    },
    {
      "name": "Helmet",
      "confidence": 90.1,
      "parents": ["Safety Equipment"]
    }
  ],
  "categorized_labels": {
    "equipment": ["Excavator"],
    "people": ["Worker"],
    "safety": ["Helmet"],
    "materials": [],
    "scene": ["Construction"],
    "other": []
  },
  "summary": {
    "total_labels": 4,
    "max_confidence": 95.5,
    "avg_confidence": 91.65,
    "top_labels": ["Construction", "Excavator", "Helmet", "Worker"],
    "has_construction_content": true
  }
}
```

### 分類結果を取得

写真の画像分類結果を取得します。

**エンドポイント**: `GET /api/v1/photos/{id}/classification`

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| id | integer | 写真ID |

**レスポンス（処理済み）**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "completed",
  "labels": [
    {
      "name": "Construction",
      "confidence": 95.5,
      "parents": []
    }
  ],
  "categorized_labels": {
    "equipment": [],
    "people": [],
    "safety": [],
    "materials": [],
    "scene": ["Construction"],
    "other": []
  },
  "summary": {
    "total_labels": 1,
    "max_confidence": 95.5,
    "avg_confidence": 95.5,
    "top_labels": ["Construction"],
    "has_construction_content": true
  }
}
```

**レスポンス（未処理）**: `200 OK`

```json
{
  "photo_id": 1,
  "status": "not_processed",
  "labels": [],
  "categorized_labels": null,
  "summary": null
}
```

---

## 検索API

### 写真を検索

複数の条件を組み合わせて写真を検索します。

**エンドポイント**: `GET /api/v1/photos/search`

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| keyword | string | × | キーワード検索（ファイル名、タイトル、説明、工種、種別） |
| work_type | string | × | 工種フィルタ |
| work_kind | string | × | 種別フィルタ |
| major_category | string | × | 写真大分類フィルタ |
| photo_type | string | × | 写真区分フィルタ |
| date_from | string | × | 撮影日開始（YYYY-MM-DD） |
| date_to | string | × | 撮影日終了（YYYY-MM-DD） |
| page | integer | × | ページ番号（デフォルト: 1） |
| page_size | integer | × | ページサイズ（デフォルト: 20、最大: 100） |

**リクエスト例**:

```
GET /api/v1/photos/search?keyword=基礎&work_type=基礎工&date_from=2024-03-01&date_to=2024-03-31&page=1&page_size=10
```

**レスポンス**: `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "file_name": "P0000001.jpg",
      "title": "基礎配筋検査",
      "work_type": "基礎工",
      ...
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

**検索ロジック**:

- `keyword`: OR条件で以下のフィールドを部分一致検索
  - file_name
  - title
  - description
  - work_type
  - work_kind
- その他のフィルタ: AND条件で完全一致
- 複数条件: 全てAND結合

---

## エラーレスポンス

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found

```json
{
  "detail": "写真が見つかりません（ID: 123）"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "file_size"],
      "msg": "Input should be a valid integer",
      "input": "invalid"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "OCR処理に失敗しました: Connection timeout"
}
```

---

## データモデル

### Photo

```typescript
interface Photo {
  id: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  s3_key: string;
  s3_url?: string;
  thumbnail_url?: string;

  title?: string;
  description?: string;
  shooting_date?: string;  // ISO 8601形式

  latitude?: string;
  longitude?: string;
  location_address?: string;

  major_category?: string;  // 写真大分類
  photo_type?: string;      // 写真区分
  work_type?: string;       // 工種
  work_kind?: string;       // 種別
  work_detail?: string;     // 細別

  tags?: string[];
  metadata?: object;

  is_processed: boolean;
  is_representative: boolean;
  is_submission_frequency: boolean;

  created_at: string;  // ISO 8601形式
  updated_at: string;  // ISO 8601形式
}
```

### BlackboardData

```typescript
interface BlackboardData {
  work_name?: string;        // 工事名
  work_type?: string;        // 工種
  work_kind?: string;        // 種別
  work_detail?: string;      // 細別
  station?: string;          // 測点
  shooting_date?: string;    // 撮影日（YYYY-MM-DD）
  design_dimension?: number; // 設計寸法（mm）
  actual_dimension?: number; // 実測寸法（mm）
  inspector?: string;        // 立会者
  remarks?: string;          // 備考
}
```

### ImageLabel

```typescript
interface ImageLabel {
  name: string;        // ラベル名
  confidence: number;  // 信頼度（0-100）
  parents: string[];   // 親カテゴリ
}
```

### ClassificationSummary

```typescript
interface ClassificationSummary {
  total_labels: number;           // 検出ラベル総数
  max_confidence: number;         // 最大信頼度
  avg_confidence: number;         // 平均信頼度
  top_labels: string[];          // 上位5ラベル
  has_construction_content: boolean;  // 建設関連コンテンツ有無
}
```

---

## 使用例

### シナリオ1: 写真アップロードからOCR処理まで

```bash
# 1. 写真メタデータを登録
curl -X POST http://localhost:8000/api/v1/photos \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "blackboard001.jpg",
    "file_size": 2048000,
    "mime_type": "image/jpeg",
    "s3_key": "photos/blackboard001.jpg"
  }'

# レスポンス: {"id": 1, ...}

# 2. OCR処理を実行
curl -X POST http://localhost:8000/api/v1/photos/1/process-ocr

# レスポンス: {"photo_id": 1, "status": "completed", "blackboard_data": {...}}

# 3. OCR結果を確認
curl http://localhost:8000/api/v1/photos/1/ocr-result

# レスポンス: {"photo_id": 1, "status": "completed", "work_name": "○○工事", ...}
```

### シナリオ2: 画像分類処理

```bash
# 1. 写真メタデータを登録
curl -X POST http://localhost:8000/api/v1/photos \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "construction_site001.jpg",
    "file_size": 3145728,
    "mime_type": "image/jpeg",
    "s3_key": "photos/construction_site001.jpg"
  }'

# レスポンス: {"id": 2, ...}

# 2. 画像分類を実行
curl -X POST http://localhost:8000/api/v1/photos/2/classify

# レスポンス: {"photo_id": 2, "status": "completed", "labels": [...], "categorized_labels": {...}, "summary": {...}}

# 3. 分類結果を確認
curl http://localhost:8000/api/v1/photos/2/classification

# レスポンス: 建設機械、作業員、安全装備などのラベル情報
```

### シナリオ3: 写真検索

```bash
# キーワード検索
curl "http://localhost:8000/api/v1/photos/search?keyword=基礎"

# 工種で絞り込み
curl "http://localhost:8000/api/v1/photos/search?work_type=基礎工"

# 日付範囲で検索
curl "http://localhost:8000/api/v1/photos/search?date_from=2024-03-01&date_to=2024-03-31"

# 複合条件検索
curl "http://localhost:8000/api/v1/photos/search?keyword=配筋&work_type=基礎工&date_from=2024-03-01&page_size=50"
```

---

## 次のステップ（Phase 2予定）

- ✅ 画像分類AI統合（Rekognition）- **完了**
- 重複写真検出
- 画質・品質自動判定
- 自動タイトル生成
- 認証・認可機能（JWT）
- S3署名付きURL生成
- WebSocket対応（リアルタイム処理状況）
- GraphQL API

---

**ドキュメント作成日**: 2025-11-02
**Phase 2 - Week 11-12: Amazon Rekognition統合完了**
