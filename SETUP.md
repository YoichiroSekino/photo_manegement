# セットアップガイド

工事写真自動整理システムの開発環境構築手順

## 📋 前提条件

以下のツールがインストールされていることを確認してください：

- **Node.js**: v18.0.0 以上
- **Python**: 3.11 以上
- **Docker**: 最新版
- **Docker Compose**: 最新版
- **Git**: 最新版

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/YoichiroSekino/photo_manegement.git
cd photo_manegement
```

### 2. 依存関係のインストール

#### ルートディレクトリ

```bash
# Prettier等の共通ツールをインストール
npm install
```

#### フロントエンド

```bash
cd frontend
npm install
cp .env.example .env.local
# .env.localを編集して、必要な環境変数を設定
```

#### バックエンド

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# .envを編集して、必要な環境変数を設定
```

### 3. Dockerコンテナの起動

```bash
# ルートディレクトリで実行
docker-compose up -d
```

これにより、以下のサービスが起動します：
- PostgreSQL (port: 5432)
- Redis (port: 6379)
- pgAdmin (port: 5050)

### 4. データベースの初期化

```bash
cd backend
# マイグレーション実行（実装後）
# python manage.py migrate
```

### 5. 開発サーバーの起動

#### フロントエンド

```bash
cd frontend
npm run dev
# http://localhost:3000 で起動
```

#### バックエンド

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload
# http://localhost:8000 で起動
```

## 🧪 テストの実行

### フロントエンド

```bash
cd frontend
npm test                # 単体テスト
npm run test:watch     # ウォッチモード
npm run test:coverage  # カバレッジレポート
```

### バックエンド

```bash
cd backend
source venv/bin/activate
pytest                    # 全テスト実行
pytest --cov=.           # カバレッジ付き
pytest -v                # 詳細表示
```

## 🔧 トラブルシューティング

### Node.jsのバージョンエラー

```bash
# nvmを使用してNode.jsバージョンを管理
nvm install 18
nvm use 18
```

### Pythonの仮想環境が見つからない

```bash
# 仮想環境を再作成
cd backend
rm -rf venv
python -m venv venv
```

### Dockerコンテナが起動しない

```bash
# コンテナをクリーンアップ
docker-compose down -v
docker-compose up -d
```

### ポートが既に使用されている

```bash
# 使用中のポートを確認
# Windows
netstat -ano | findstr :3000

# macOS/Linux
lsof -i :3000
```

## 📚 次のステップ

- [開発ガイド](./CONTRIBUTING.md)を読む
- [実装ガイドライン](./docs/implementation-guide.md)を確認
- [GitHub Issues](https://github.com/YoichiroSekino/photo_manegement/issues)でタスクを確認

## 🆘 サポート

問題が発生した場合：

1. [GitHub Issues](https://github.com/YoichiroSekino/photo_manegement/issues)で既存の問題を確認
2. 新しいissueを作成して詳細を報告
3. プロジェクトメンテナーに連絡

---

**更新日**: 2025-11-02
