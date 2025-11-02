# データベースマイグレーションガイド

このプロジェクトでは Alembic を使用してデータベースマイグレーションを管理しています。

## セットアップ

Alembicはすでに初期化されています。

## マイグレーションコマンド

### 1. 新しいマイグレーションを作成

モデルの変更後、自動的にマイグレーションファイルを生成:

```bash
cd backend
./venv/Scripts/alembic revision --autogenerate -m "マイグレーションの説明"
```

### 2. マイグレーションを適用

最新バージョンにアップグレード:

```bash
./venv/Scripts/alembic upgrade head
```

### 3. マイグレーションをロールバック

1つ前のバージョンにダウングレード:

```bash
./venv/Scripts/alembic downgrade -1
```

特定のリビジョンまでダウングレード:

```bash
./venv/Scripts/alembic downgrade <revision_id>
```

### 4. 現在のマイグレーション状態を確認

```bash
./venv/Scripts/alembic current
```

### 5. マイグレーション履歴を確認

```bash
./venv/Scripts/alembic history
```

## データベース接続設定

データベース接続URLは `alembic.ini` で設定されています:

```ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/construction_photos
```

本番環境では環境変数を使用することを推奨します。

## 初回セットアップ手順

1. **データベースを作成** (PostgreSQL):

```sql
CREATE DATABASE construction_photos;
```

2. **マイグレーションを適用**:

```bash
cd backend
./venv/Scripts/alembic upgrade head
```

3. **確認**:

```bash
./venv/Scripts/alembic current
```

## トラブルシューティング

### マイグレーションがスキップされる

モデルのインポートが正しいか確認:

```python
# alembic/env.py
from app.database.models import Base
target_metadata = Base.metadata
```

### データベース接続エラー

1. PostgreSQLが起動しているか確認
2. `alembic.ini` の接続URLが正しいか確認
3. データベースが存在するか確認

### マイグレーションの競合

```bash
# マイグレーションヘッドを確認
./venv/Scripts/alembic heads

# ブランチをマージ
./venv/Scripts/alembic merge <rev1> <rev2> -m "Merge branches"
```

## ベストプラクティス

1. **マイグレーション前にバックアップ**: 本番環境では必ずデータをバックアップ
2. **テスト環境で確認**: まずテスト環境でマイグレーションを実行
3. **ロールバック計画**: ダウングレードスクリプトも必ず確認
4. **コミット**: マイグレーションファイルはGitで管理
5. **レビュー**: 自動生成されたマイグレーションは必ずレビュー
