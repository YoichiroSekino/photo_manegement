"""
写真APIエンドポイントのテスト
"""

import pytest
from datetime import datetime


def test_create_photo(client):
    """写真作成APIのテスト"""
    photo_data = {
        "file_name": "test.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/test.jpg",
        "title": "テスト写真",
    }

    response = client.post("/api/v1/photos", json=photo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "test.jpg"
    assert data["title"] == "テスト写真"
    assert "id" in data


def test_get_photos_list(client):
    """写真一覧取得APIのテスト"""
    response = client.get("/api/v1/photos")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_get_photo_by_id(client):
    """写真詳細取得APIのテスト"""
    # まず写真を作成
    photo_data = {
        "file_name": "test2.jpg",
        "file_size": 2048000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/test2.jpg",
    }
    create_response = client.post("/api/v1/photos", json=photo_data)
    photo_id = create_response.json()["id"]

    # 作成した写真を取得
    response = client.get(f"/api/v1/photos/{photo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == photo_id
    assert data["file_name"] == "test2.jpg"


def test_get_nonexistent_photo(client):
    """存在しない写真の取得テスト"""
    response = client.get("/api/v1/photos/99999")
    assert response.status_code == 404
