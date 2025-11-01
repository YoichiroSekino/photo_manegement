"""
データベース接続設定
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# データベースURL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/construction_photos"
)

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 接続チェック
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """データベースセッションを取得する依存関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
