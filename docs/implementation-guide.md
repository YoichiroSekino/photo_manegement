# 実装ガイドライン

**バージョン**: 1.0
**作成日**: 2025-11-02
**対象**: 工事写真自動整理システム開発チーム

---

## 目次

1. [開発環境セットアップ](#1-開発環境セットアップ)
2. [コーディング規約](#2-コーディング規約)
3. [Git運用ルール](#3-git運用ルール)
4. [テスト戦略](#4-テスト戦略)
5. [デプロイ手順](#5-デプロイ手順)
6. [監視・ログ戦略](#6-監視ログ戦略)
7. [セキュリティベストプラクティス](#7-セキュリティベストプラクティス)

---

## 1. 開発環境セットアップ

### 1.1 必須ツールインストール

```bash
# Node.js (v18以上)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Python (3.11以上)
pyenv install 3.11.0
pyenv global 3.11.0

# Docker & Docker Compose
# https://docs.docker.com/get-docker/

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Terraform
brew install terraform  # macOS
# or
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 1.2 リポジトリクローン・初期設定

```bash
# リポジトリクローン
git clone https://github.com/your-org/photo-management.git
cd photo-management

# フロントエンド セットアップ
cd frontend
npm install
cp .env.example .env.local
# .env.localを編集（AWS認証情報等）

# バックエンド セットアップ
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Docker コンテナ起動（PostgreSQL, Redis）
docker-compose up -d

# データベースマイグレーション
npm run db:migrate  # or python manage.py migrate
```

### 1.3 VS Code 推奨拡張機能

```json
// .vscode/extensions.json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-azuretools.vscode-docker",
    "amazonwebservices.aws-toolkit-vscode",
    "bradlc.vscode-tailwindcss",
    "formulahendry.auto-rename-tag",
    "eamodio.gitlens"
  ]
}
```

### 1.4 VS Code 設定

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.rulers": [88]
  },
  "[typescript]": {
    "editor.rulers": [100]
  },
  "[typescriptreact]": {
    "editor.rulers": [100]
  }
}
```

---

## 2. コーディング規約

### 2.1 TypeScript/React 規約

#### ファイル命名

```
コンポーネント: PascalCase
  ✓ PhotoUploader.tsx
  ✗ photoUploader.tsx
  ✗ photo-uploader.tsx

Hooks: camelCase + use prefix
  ✓ usePhotos.ts
  ✓ useUpload.ts

Utils: camelCase
  ✓ formatDate.ts
  ✓ validateFile.ts

Types: PascalCase + .types.ts
  ✓ Photo.types.ts
```

#### コンポーネント構造

```typescript
// components/photos/PhotoCard.tsx
import { FC } from 'react';
import { Photo } from '@/types/photo.types';

// Props型定義
interface PhotoCardProps {
  photo: Photo;
  onSelect?: (id: string) => void;
}

/**
 * 写真カードコンポーネント
 *
 * @param photo - 表示する写真データ
 * @param onSelect - 選択時のコールバック
 */
export const PhotoCard: FC<PhotoCardProps> = ({ photo, onSelect }) => {
  // ✓ フックは先頭にまとめる
  const [isHovered, setIsHovered] = useState(false);
  const { formatDate } = useDateFormatter();

  // ✓ イベントハンドラー
  const handleClick = useCallback(() => {
    onSelect?.(photo.id);
  }, [photo.id, onSelect]);

  // ✓ 条件付きレンダリングは早期リターン
  if (!photo) return null;

  // ✓ JSXは読みやすく整形
  return (
    <div
      className="photo-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      <img src={photo.thumbnailUrl} alt={photo.title} />
      <div className="photo-card__info">
        <h3>{photo.title}</h3>
        <p>{formatDate(photo.shootingDate)}</p>
      </div>
    </div>
  );
};
```

#### Hooks 規約

```typescript
// hooks/usePhotos.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface UsePhotosOptions {
  category?: string;
  limit?: number;
}

/**
 * 写真一覧取得フック
 */
export function usePhotos(options: UsePhotosOptions = {}) {
  // ✓ useQueryのキーは配列で明示的に
  return useQuery({
    queryKey: ['photos', options],
    queryFn: () => apiClient.getPhotos(options),
    staleTime: 5 * 60 * 1000, // 5分
    // ✓ エラーハンドリング
    onError: (error) => {
      console.error('Failed to fetch photos:', error);
    },
  });
}
```

#### 型定義規約

```typescript
// types/photo.types.ts

/**
 * 写真エンティティ
 */
export interface Photo {
  id: string;
  fileName: string;
  title: string;
  category: PhotoCategory;
  uploadDate: string; // ISO 8601
  shootingDate: string; // YYYY-MM-DD
  location?: GeoLocation;
  ocrData?: OCRData;
  qualityScore?: number;
}

/**
 * 写真カテゴリ
 */
export type PhotoCategory =
  | '着手前及び完成写真'
  | '施工状況写真'
  | '安全管理写真'
  | '使用材料写真'
  | '品質管理写真'
  | '出来形管理写真'
  | '災害写真'
  | 'その他';

/**
 * 位置情報
 */
export interface GeoLocation {
  latitude: number;
  longitude: number;
  accuracy?: number; // meters
}

/**
 * OCRデータ
 */
export interface OCRData {
  rawText: string;
  confidence: number;
  metadata: {
    projectName?: string;
    workType?: string;
    stationNumber?: string;
    shootingDate?: string;
  };
}

// ✓ API レスポンス型
export interface PhotoListResponse {
  total: number;
  photos: Photo[];
  hasMore: boolean;
}

// ✓ APIリクエスト型
export interface CreatePhotoRequest {
  fileName: string;
  fileSize: number;
  contentType: string;
}
```

### 2.2 Python/FastAPI 規約

#### ファイル構成

```
backend/
├── api/
│   └── routes/
│       └── photos.py          # ルート定義
├── domain/
│   ├── models/
│   │   └── photo.py           # ドメインモデル
│   ├── services/
│   │   └── photo_service.py   # ビジネスロジック
│   └── repositories/
│       └── photo_repository.py # データアクセス
└── infrastructure/
    └── aws/
        └── s3_client.py       # インフラ層
```

#### コーディングスタイル

```python
# domain/services/photo_service.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PhotoService:
    """写真管理サービス"""

    def __init__(self, repository: PhotoRepository, s3_client: S3Client):
        """
        Args:
            repository: 写真リポジトリ
            s3_client: S3クライアント
        """
        self.repository = repository
        self.s3_client = s3_client

    def create_photo(
        self,
        user_id: str,
        file_name: str,
        file_size: int
    ) -> Photo:
        """
        写真を作成

        Args:
            user_id: ユーザーID
            file_name: ファイル名
            file_size: ファイルサイズ（バイト）

        Returns:
            作成された写真

        Raises:
            ValueError: ファイル名が不正な場合
            StorageError: S3アップロード失敗
        """
        # ✓ バリデーション
        if not self._validate_filename(file_name):
            raise ValueError(f"Invalid filename: {file_name}")

        # ✓ S3キー生成
        photo_id = str(uuid.uuid4())
        s3_key = f"uploads/{photo_id}/{file_name}"

        # ✓ Presigned URL生成
        upload_url = self.s3_client.generate_presigned_url(
            bucket="construction-photos",
            key=s3_key,
            expires_in=900  # 15分
        )

        # ✓ DB保存
        photo = Photo(
            id=photo_id,
            user_id=user_id,
            file_name=file_name,
            s3_key=s3_key,
            file_size=file_size,
            upload_date=datetime.utcnow(),
            status="uploading"
        )

        self.repository.create(photo)

        return photo

    def _validate_filename(self, filename: str) -> bool:
        """ファイル名検証（プライベートメソッド）"""
        import re
        # 許可する拡張子
        allowed_extensions = {'.jpg', '.jpeg', '.tif', '.tiff'}
        ext = Path(filename).suffix.lower()
        return ext in allowed_extensions
```

#### Type Hints必須

```python
# ✓ Good
def process_photo(photo_id: str, options: Dict[str, Any]) -> ProcessingResult:
    pass

# ✗ Bad
def process_photo(photo_id, options):
    pass
```

#### Docstring (Google Style)

```python
def calculate_quality_score(
    image_path: str,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    画像品質スコアを計算

    Args:
        image_path: 画像ファイルパス
        weights: 評価項目の重み（省略時はデフォルト）

    Returns:
        品質スコア（0-100）

    Raises:
        FileNotFoundError: 画像ファイルが存在しない場合
        ValueError: 画像形式が不正な場合

    Example:
        >>> score = calculate_quality_score('photo.jpg')
        >>> print(score)
        85.3
    """
    pass
```

### 2.3 コード品質チェック

#### ESLint設定

```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": ["warn", { "allow": ["error", "warn"] }]
  }
}
```

#### Pylint/Black設定

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.pylint.messages_control]
disable = [
    "C0111",  # missing-docstring
    "R0903",  # too-few-public-methods
]

[tool.pylint.format]
max-line-length = 88
```

---

## 3. Git運用ルール

### 3.1 ブランチ戦略（GitHub Flow）

```
main (保護ブランチ)
  │
  ├─ feature/photo-upload
  ├─ feature/ocr-integration
  ├─ fix/search-bug
  └─ hotfix/security-patch
```

#### ブランチ命名規則

```
feature/{issue-number}-{short-description}
  例: feature/123-photo-upload

fix/{issue-number}-{bug-description}
  例: fix/456-search-performance

hotfix/{critical-issue}
  例: hotfix/security-s3-access

chore/{task-description}
  例: chore/update-dependencies
```

### 3.2 コミットメッセージ規約

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type一覧

```
feat:     新機能
fix:      バグ修正
docs:     ドキュメントのみの変更
style:    コードの意味に影響を与えない変更（空白、フォーマット等）
refactor: リファクタリング
perf:     パフォーマンス改善
test:     テストの追加・修正
chore:    ビルドプロセスやツールの変更
```

#### 例

```bash
# Good
git commit -m "feat(upload): add drag-and-drop file upload

- Implement DragDropZone component
- Add file validation (JPEG, TIFF only)
- Support up to 10,000 files

Closes #123"

# Bad
git commit -m "update"
git commit -m "fix bug"
```

### 3.3 プルリクエスト（PR）ルール

#### PRテンプレート

```markdown
## 概要
<!-- このPRで何を変更するか -->

## 変更内容
- [ ] 新機能A
- [ ] バグ修正B
- [ ] リファクタリングC

## テスト
- [ ] 単体テスト追加
- [ ] 結合テスト実施
- [ ] 手動テスト完了

## スクリーンショット（UI変更の場合）
<!-- Before/After画像 -->

## チェックリスト
- [ ] ESLint/Pylintエラーなし
- [ ] テストがすべてパス
- [ ] ドキュメント更新済み
- [ ] CLAUDE.md確認済み

## 関連Issue
Closes #123
```

#### レビュー基準

```
必須チェック項目:
1. コードが仕様を満たしているか
2. テストが十分か（カバレッジ80%以上）
3. セキュリティ上の問題はないか
4. パフォーマンスへの影響は許容範囲か
5. コーディング規約に準拠しているか

承認条件:
- 少なくとも1名のApprove
- CI/CDテストがすべてパス
- コンフリクトがない
```

---

## 4. テスト戦略

### 4.1 テストピラミッド

```
        /\
       /E2E\          10% - クリティカルパスのみ
      /------\
     /  統合  \        30% - API、DB連携
    /----------\
   /   単体    \      60% - ロジック、関数
  /--------------\
```

### 4.2 単体テスト（Jest）

```typescript
// __tests__/utils/validateFile.test.ts
import { validateFile } from '@/utils/validateFile';

describe('validateFile', () => {
  it('should accept JPEG files', () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' });
    expect(validateFile(file)).toBe(true);
  });

  it('should reject PNG files', () => {
    const file = new File([''], 'test.png', { type: 'image/png' });
    expect(validateFile(file)).toBe(false);
  });

  it('should reject files larger than 10MB', () => {
    const largeContent = new Array(11 * 1024 * 1024).fill('a').join('');
    const file = new File([largeContent], 'large.jpg', { type: 'image/jpeg' });
    expect(validateFile(file)).toBe(false);
  });

  it('should accept files with valid pixel count', () => {
    // ... implementation
  });
});
```

#### カバレッジ目標

```json
// jest.config.js
{
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

### 4.3 統合テスト（Pytest）

```python
# tests/integration/test_photo_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """認証ヘッダーを返す"""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

def test_create_photo(auth_headers):
    """写真作成APIテスト"""
    response = client.post(
        "/api/v1/photos/upload",
        json={
            "fileName": "test.jpg",
            "fileSize": 2048576,
            "contentType": "image/jpeg"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "photoId" in data
    assert "uploadUrl" in data

def test_get_photos_with_filter(auth_headers):
    """写真一覧取得（フィルタ付き）テスト"""
    response = client.get(
        "/api/v1/photos?category=施工状況写真&limit=50",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
    assert len(data["photos"]) <= 50
```

### 4.4 E2Eテスト（Playwright）

```typescript
// e2e/upload.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Photo Upload Flow', () => {
  test('should upload photos successfully', async ({ page }) => {
    // ログイン
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');

    // アップロードページに移動
    await page.goto('/upload');

    // ファイル選択
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      'fixtures/sample1.jpg',
      'fixtures/sample2.jpg',
    ]);

    // アップロード開始
    await page.click('button:has-text("アップロード開始")');

    // 完了を待機
    await expect(page.locator('text=2枚のアップロード完了')).toBeVisible({
      timeout: 30000,
    });

    // 写真一覧に表示されることを確認
    await page.goto('/photos');
    await expect(page.locator('.photo-card')).toHaveCount(2, { timeout: 5000 });
  });
});
```

### 4.5 テスト実行コマンド

```bash
# フロントエンド
npm run test              # 単体テスト
npm run test:watch        # watch mode
npm run test:coverage     # カバレッジ
npm run test:e2e          # E2Eテスト

# バックエンド
pytest                    # 全テスト
pytest -v                 # 詳細表示
pytest --cov=app          # カバレッジ
pytest -k "test_photo"    # 特定のテストのみ
```

---

## 5. デプロイ手順

### 5.1 CI/CD パイプライン（GitHub Actions）

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run linter
        run: npm run lint

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Next.js
        run: |
          npm ci
          npm run build

      - name: Deploy to S3
        run: |
          aws s3 sync out/ s3://construction-photos-frontend --delete

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} \
            --paths "/*"

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy Lambda
        run: |
          cd backend
          zip -r function.zip .
          aws lambda update-function-code \
            --function-name photo-upload \
            --zip-file fileb://function.zip
```

### 5.2 環境別デプロイ

| 環境 | ブランチ | デプロイ方法 | 用途 |
|------|---------|------------|------|
| **開発** | feature/* | 自動デプロイ | 開発者テスト |
| **ステージング** | develop | 自動デプロイ | QA・受入テスト |
| **本番** | main | 承認後デプロイ | 本番運用 |

---

## 6. 監視・ログ戦略

### 6.1 CloudWatch Logs

```python
# shared/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON形式でログ出力"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)

# 使用例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

logger.info("Photo uploaded", extra={"photo_id": "123", "file_size": 2048576})
```

### 6.2 メトリクス監視

```python
# monitoring/metrics.py
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name: str, value: float, unit: str = 'Count'):
    """カスタムメトリクス送信"""
    cloudwatch.put_metric_data(
        Namespace='PhotoManagement',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
        ]
    )

# 使用例
put_metric('PhotosProcessed', 100, 'Count')
put_metric('OCRAccuracy', 0.87, 'Percent')
```

---

## 7. セキュリティベストプラクティス

### 7.1 環境変数管理

```bash
# ✓ Good - 環境変数
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# ✗ Bad - ハードコード
const accessKey = 'AKIAIOSFODNN7EXAMPLE';  // 絶対NG
```

### 7.2 機密情報の取り扱い

```typescript
// ✓ Good
const apiKey = process.env.GOOGLE_MAPS_API_KEY;

// ✗ Bad
const apiKey = 'AIzaSyDxxxxxxxxxxxxxx';  // 絶対NG
```

### 7.3 入力バリデーション

```python
from pydantic import BaseModel, validator

class CreatePhotoRequest(BaseModel):
    fileName: str
    fileSize: int

    @validator('fileName')
    def validate_filename(cls, v):
        # パストラバーサル対策
        if '..' in v or '/' in v:
            raise ValueError("Invalid filename")
        return v

    @validator('fileSize')
    def validate_filesize(cls, v):
        if v > 10 * 1024 * 1024:  # 10MB
            raise ValueError("File too large")
        return v
```

---

**開発チームは本ガイドラインに従って実装を進めてください。**
