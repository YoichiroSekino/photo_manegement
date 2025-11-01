"""
メインAPIのテスト
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """テストクライアントのfixture"""
    from app.main import app

    return TestClient(app)


def test_read_root(client):
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "工事写真自動整理システム API"


def test_health_check(client):
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_api_info(client):
    """API情報エンドポイントのテスト"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Construction Photo Management API"
