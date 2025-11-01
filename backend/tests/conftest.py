"""
Pytestの共通フィクスチャ設定
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.models import Base
from app.database.database import get_db
from app.main import app

# テスト用インメモリデータベース（全テストで共有するため、check_same_thread=Falseが必要）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 同じ接続を使い回す
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """テスト前にテーブルを作成、テスト後に削除"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """テスト用データベースセッション"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db):
    """テストクライアント"""

    def override_get_db():
        try:
            yield db
        finally:
            pass  # dbのcloseはdb fixtureに任せる

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # クリーンアップ
        app.dependency_overrides.clear()
