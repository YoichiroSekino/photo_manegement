# マルチテナント実装ガイド

## 概要

このドキュメントは、工事写真自動整理システムのマルチテナント機能の実装詳細を説明します。

**実装パターン**: Shared Database with Row-Level Security (共有データベース + 行レベルセキュリティ)

## 実装完了日

2025-11-02

## アーキテクチャ

### データベース層

#### 1. Organizationモデル

```python
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**特徴**:
- サブドメインでテナントを識別
- `is_active`フラグで組織の有効/無効を管理

#### 2. 既存モデルへのorganization_id追加

以下のモデルに`organization_id`カラムを追加:
- `Photo`
- `User`
- `Project` (将来実装)
- `PhotoDuplicate` (重複検出データ)

**外部キー制約**:
```sql
FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
```

**インデックス**:
- 単一カラムインデックス: `organization_id`
- 複合インデックス:
  - `(organization_id, created_at)`
  - `(organization_id, shooting_date)`

### 認証層

#### JWT拡張

アクセストークンとリフレッシュトークンに`org_id`フィールドを追加:

```python
def create_tokens(user_id: int, email: str, organization_id: int):
    access_token = JWTHandler.create_access_token(
        data={"sub": str(user_id), "email": email, "org_id": organization_id}
    )
    refresh_token = JWTHandler.create_refresh_token(
        data={"sub": str(user_id), "email": email, "org_id": organization_id}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
```

### API層

#### 認証とテナントフィルタの追加

全ての主要APIエンドポイントに以下を適用:

1. **認証必須化**: `current_user: User = Depends(get_current_active_user)`
2. **テナントフィルタ**: `Photo.organization_id == current_user.organization_id`

**修正済みAPIルーター**:
- ✅ `app/routers/photos.py` (写真CRUD)
- ✅ `app/routers/search.py` (検索)
- ✅ `app/routers/ocr.py` (OCR処理)
- ✅ `app/routers/rekognition.py` (画像認識)
- ✅ `app/routers/export.py` (エクスポート)

**実装例** (`photos.py:143-163`):
```python
@router.get("", response_model=PhotoListResponse)
async def get_photos(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # テナントフィルタ適用
    query = db.query(Photo).filter(Photo.organization_id == current_user.organization_id)
    total = query.count()
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    photos = query.offset(skip).limit(page_size).all()

    return PhotoListResponse(
        items=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
```

### ミドルウェア層

#### テナント識別ミドルウェア

**ファイル**: `app/middleware/tenant_middleware.py`

**識別方法（優先順位順）**:
1. `X-Organization-Subdomain` ヘッダー (APIクライアント用)
2. サブドメイン (Webアプリ用、例: `companya.example.com`)
3. デフォルト組織 (開発環境用)

**スキップパス**:
- `/docs`, `/redoc`, `/openapi.json`
- `/health`
- `/api/v1/auth/login`, `/api/v1/auth/register`

**動作**:
```python
# 組織情報をrequest.stateに設定
request.state.organization = organization
request.state.organization_id = organization.id
request.state.organization_subdomain = organization.subdomain

# レスポンスヘッダーに組織情報を追加（デバッグ用）
response.headers["X-Organization-ID"] = str(organization.id)
response.headers["X-Organization-Subdomain"] = organization.subdomain
```

### ストレージ層

#### S3キー構造の変更

**変更前**:
```
photos/{timestamp}_{filename}
```

**変更後**:
```
organizations/{organization_id}/photos/{timestamp}_{filename}
```

**実装箇所**: `app/routers/photos.py:66-69`

**メリット**:
- 組織ごとのデータ物理的分離
- S3バケットポリシーでの細かいアクセス制御が可能
- データ移行・削除が容易

## データベースマイグレーション

### マイグレーションファイル

**ファイル**: `alembic/versions/6c9f69f2b32f_add_multitenant_support_organizations_and_relationships.py`

**処理内容**:

1. **organizationsテーブル作成**
2. **デフォルト組織作成** (既存データ用)
   ```sql
   INSERT INTO organizations (name, subdomain, is_active)
   VALUES ('Default Organization', 'default', 1)
   ```
3. **既存テーブルにorganization_id追加**
   - photos, users, projects, photo_duplicates
   - 既存データをデフォルト組織（ID=1）に紐付け
4. **外部キー制約とインデックス追加**
5. **複合インデックス追加**

**実行**:
```bash
./venv/Scripts/alembic upgrade head
```

## テスト

### マルチテナントテスト

#### 1. 写真API (`tests/test_api_photos_multitenant.py`)

**テストケース** (4/4 passed):
- ✅ 写真作成時にorganization_idが自動設定される
- ✅ 写真一覧が組織でフィルタリングされる
- ✅ 写真詳細取得が同じ組織のみアクセス可能
- ✅ 認証なしアクセスは拒否される

#### 2. 検索API (`tests/test_api_search_multitenant.py`)

**テストケース** (4/4 passed):
- ✅ 全写真検索が組織でフィルタリングされる
- ✅ キーワード検索が組織でフィルタリングされる
- ✅ フィルタ検索が組織でフィルタリングされる
- ✅ 認証なし検索は拒否される

#### 3. JWT認証 (`tests/test_jwt_multitenant.py`)

**テストケース** (6/6 passed):
- ✅ organization_idを含むトークン作成
- ✅ アクセストークンにorganization_id含まれる
- ✅ リフレッシュトークンにorganization_id含まれる
- ✅ 異なる組織は異なるトークンを持つ
- ✅ organization_idなしのトークンも動作する（後方互換性）

### テスト実行方法

```bash
# 全マルチテナントテスト実行
./venv/Scripts/pytest tests/test_*_multitenant.py -v

# カバレッジ付き実行
./venv/Scripts/pytest --cov=app --cov-report=term-missing
```

## セキュリティ

### 実装済みセキュリティ対策

1. **認証必須化**
   - 全ての主要APIエンドポイントで認証必須
   - HTTPBearer認証方式

2. **テナント分離**
   - データベース行レベルでのフィルタリング
   - `organization_id`による厳格なアクセス制御
   - 他組織のデータへのアクセス試行は404エラー

3. **S3データ分離**
   - 組織ごとのフォルダ分け
   - 将来的にS3バケットポリシーで制御可能

4. **JWT検証**
   - トークンにorganization_id含む
   - トークン検証時に組織情報も検証

### セキュリティ考慮事項

#### ✅ 実装済み

- SQL injection対策: ORMによるパラメータ化クエリ
- 認証トークンの有効期限管理
- パスワードハッシュ化 (bcrypt)
- CORS設定

#### 🔄 今後の強化推奨

- Rate limiting (既にSlowAPIで実装済み)
- API Key管理
- S3バケットポリシーの設定
- データ暗号化 (at rest / in transit)
- 監査ログ

## 使用方法

### 1. 新規組織の作成

```python
from app.database.models import Organization

org = Organization(
    name="Company A",
    subdomain="companya",
    is_active=True
)
db.add(org)
db.commit()
```

### 2. APIアクセス（ヘッダー指定）

```bash
# ヘッダーでテナント指定
curl -X GET "http://localhost:8000/api/v1/photos" \
  -H "Authorization: Bearer {access_token}" \
  -H "X-Organization-Subdomain: companya"
```

### 3. サブドメインでのアクセス

```bash
# サブドメインでテナント識別
curl -X GET "http://companya.example.com/api/v1/photos" \
  -H "Authorization: Bearer {access_token}"
```

### 4. 写真アップロード

```python
# フロントエンドから
const response = await fetch('/api/v1/photos/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'X-Organization-Subdomain': 'companya',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    fileName: 'photo.jpg',
    fileSize: 1024000,
    mimeType: 'image/jpeg'
  })
});

const { presignedUrl, key } = await response.json();

// S3に直接アップロード
await fetch(presignedUrl, {
  method: 'PUT',
  body: file,
  headers: {
    'Content-Type': 'image/jpeg'
  }
});

// DBに写真レコード作成
await fetch('/api/v1/photos', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'X-Organization-Subdomain': 'companya',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    file_name: 'photo.jpg',
    file_size: 1024000,
    mime_type: 'image/jpeg',
    s3_key: key  // Presigned URL生成時に受け取ったキー
  })
});
```

## パフォーマンス

### インデックス最適化

#### 単一カラムインデックス
```sql
CREATE INDEX ix_photos_organization_id ON photos(organization_id);
CREATE INDEX ix_users_organization_id ON users(organization_id);
```

#### 複合インデックス
```sql
CREATE INDEX ix_photos_org_created ON photos(organization_id, created_at);
CREATE INDEX ix_photos_org_shooting_date ON photos(organization_id, shooting_date);
```

### クエリパフォーマンス

**想定負荷**:
- 組織数: 1,000
- 1組織あたりの写真数: 最大200,000枚
- 同時アクセスユーザー数: 1,000

**最適化施策**:
1. organization_idでのフィルタリングが必ず先頭
2. 複合インデックスによるカバリングインデックス効果
3. ページネーション必須（デフォルト20件/ページ）

## トラブルシューティング

### 1. 組織が見つからないエラー

**エラー**: `404 Not Found: 組織が見つかりません`

**原因**:
- 無効なサブドメイン指定
- 組織が`is_active=False`

**解決方法**:
```python
# 組織の確認
org = db.query(Organization).filter(Organization.subdomain == "companya").first()
if org:
    print(f"組織名: {org.name}, アクティブ: {org.is_active}")
else:
    print("組織が存在しません")
```

### 2. 他組織のデータが見える

**原因**: テナントフィルタが適用されていない

**チェックポイント**:
```python
# 必ずorganization_idでフィルタ
query = db.query(Photo).filter(Photo.organization_id == current_user.organization_id)

# ❌ 誤った実装
query = db.query(Photo)  # organization_idフィルタなし
```

### 3. S3アップロード時のキーエラー

**エラー**: S3キーに組織IDが含まれていない

**原因**: アップロードエンドポイントが認証なしで呼ばれている

**解決方法**:
- `/api/v1/photos/upload`に必ずAuthorizationヘッダーを付ける
- organization_idはcurrent_userから自動取得される

## まとめ

### 実装済み機能

✅ **Phase 1: データベース層**
- Organization モデル作成
- 既存モデルへのorganization_id追加
- データ移行スクリプト
- JWT認証拡張

✅ **Phase 2: API層**
- 写真API修正（テナントフィルタ）
- 検索API修正（テナントフィルタ）
- OCR/Rekognition API修正
- エクスポートAPI修正

✅ **Phase 3: インフラ層**
- テナント識別ミドルウェア作成
- S3キー構造変更（組織ごとの分離）

### 今後の拡張

🔄 **Phase 4: テストとドキュメント**
- 統合テスト追加
- パフォーマンステスト
- セキュリティテスト

🔄 **Phase 5: 管理機能**
- 組織管理UI
- ユーザー招待機能
- 組織間データ移行ツール

## 参考資料

- [FastAPI Multi-tenancy Guide](https://fastapi.tiangolo.com/)
- [SQLAlchemy Row Level Security](https://docs.sqlalchemy.org/)
- [AWS S3 Multi-tenant Data Isolation](https://aws.amazon.com/blogs/security/)

---

**作成者**: Claude Code
**最終更新**: 2025-11-02
