-- 工事写真管理システム - データベース初期化スクリプト

-- PostGIS拡張を有効化（位置情報管理用）
-- Note: PostGISが必要な場合は、postgis/postgisイメージを使用してください
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- タイムゾーン設定
SET timezone = 'Asia/Tokyo';

-- スキーマ作成
CREATE SCHEMA IF NOT EXISTS construction_photos;

-- 開発用テーブル作成（基本構造のみ）
-- 注: 詳細なスキーマはAlembicマイグレーションで管理

-- バージョン管理テーブル
CREATE TABLE IF NOT EXISTS construction_photos.schema_version (
    version_id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 初期バージョンレコード挿入
INSERT INTO construction_photos.schema_version (version, description)
VALUES ('0.1.0', 'Initial database setup')
ON CONFLICT DO NOTHING;

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_schema_version_applied_at
ON construction_photos.schema_version(applied_at);

-- コメント追加
COMMENT ON SCHEMA construction_photos IS '工事写真管理システムのデータスキーマ';
COMMENT ON TABLE construction_photos.schema_version IS 'データベーススキーマのバージョン管理';

-- 正常終了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END $$;
