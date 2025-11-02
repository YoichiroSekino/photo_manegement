"""
写真APIエンドポイントのテスト（マルチテナント対応）
"""

import pytest
from datetime import datetime
from app.database.models import Organization, User
from app.auth.jwt_handler import create_tokens


class TestPhotosAPI:
    """写真API テスト"""

    @pytest.fixture
    def test_org(self, db):
        """テスト用組織"""
        org = Organization(name="Test Company", subdomain="testcompany", is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    @pytest.fixture
    def test_user(self, db, test_org):
        """テスト用ユーザー"""
        user = User(
            email="test@testcompany.com",
            hashed_password="hashed",
            organization_id=test_org.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダー"""
        tokens = create_tokens(test_user.id, test_user.email, test_user.organization_id)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def test_create_photo(self, client, auth_headers):
        """写真作成APIのテスト"""
        photo_data = {
            "file_name": "test.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/test.jpg",
            "title": "テスト写真",
        }

        response = client.post("/api/v1/photos", json=photo_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["file_name"] == "test.jpg"
        assert data["title"] == "テスト写真"
        assert "id" in data
        assert "organization_id" in data

    def test_get_photos_list(self, client, auth_headers):
        """写真一覧取得APIのテスト"""
        response = client.get("/api/v1/photos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_get_photo_by_id(self, client, auth_headers):
        """写真詳細取得APIのテスト"""
        # まず写真を作成
        photo_data = {
            "file_name": "test2.jpg",
            "file_size": 2048000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/test2.jpg",
        }
        create_response = client.post(
            "/api/v1/photos", json=photo_data, headers=auth_headers
        )
        photo_id = create_response.json()["id"]

        # 作成した写真を取得
        response = client.get(f"/api/v1/photos/{photo_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == photo_id
        assert data["file_name"] == "test2.jpg"

    def test_get_nonexistent_photo(self, client, auth_headers):
        """存在しない写真の取得テスト"""
        response = client.get("/api/v1/photos/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_create_photo_invalid_mime_type(self, client, auth_headers):
        """無効なMIMEタイプでの写真作成テスト"""
        photo_data = {
            "file_name": "test_invalid.png",
            "file_size": 1024000,
            "mime_type": "image/png",  # 無効（許可されていない形式）
            "s3_key": "photos/test_invalid.png",
        }

        response = client.post("/api/v1/photos", json=photo_data, headers=auth_headers)
        assert response.status_code == 422  # Validation Error
        assert "mime_type" in response.json()["detail"][0]["loc"]

    def test_unauthenticated_access(self, client):
        """認証なしアクセスは拒否される"""
        # 認証なしで写真一覧にアクセス
        response = client.get("/api/v1/photos")
        assert response.status_code == 403  # HTTPBearer returns 403

        # 認証なしで写真作成
        photo_data = {
            "file_name": "test.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/test.jpg",
        }
        response = client.post("/api/v1/photos", json=photo_data)
        assert response.status_code == 403
