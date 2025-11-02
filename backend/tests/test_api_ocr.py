"""
OCR処理APIエンドポイントのテスト（マルチテナント対応）
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ocr_service import BlackboardData
from app.database.models import Organization, User
from app.auth.jwt_handler import create_tokens


class TestOCRAPI:
    """OCR API テスト"""

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

    def test_process_ocr(self, client, auth_headers):
        """OCR処理トリガーAPIのテスト"""
        # まず写真を作成
        photo_data = {
            "file_name": "blackboard.jpg",
            "file_size": 2048000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/blackboard.jpg",
        }
        create_response = client.post(
            "/api/v1/photos", json=photo_data, headers=auth_headers
        )
        photo_id = create_response.json()["id"]

        # Mock OCR service
        mock_blackboard_data = BlackboardData(
            work_name="テスト工事",
            work_type="土工",
            station="100+5.0",
            shooting_date="2024-03-15",
        )

        with patch("app.routers.ocr.OCRService") as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.extract_text_from_image.return_value = [
                {"text": "テスト工事", "confidence": 95.0}
            ]
            mock_ocr.parse_blackboard_text.return_value = mock_blackboard_data
            mock_ocr_class.return_value = mock_ocr

            # OCR処理をトリガー
            response = client.post(
                f"/api/v1/photos/{photo_id}/process-ocr", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["photo_id"] == photo_id
            assert data["status"] == "completed"
            assert data["blackboard_data"]["work_name"] == "テスト工事"
            assert data["blackboard_data"]["work_type"] == "土工"

    def test_get_ocr_result(self, client, auth_headers):
        """OCR結果取得APIのテスト"""
        # 写真を作成してOCR処理
        photo_data = {
            "file_name": "blackboard.jpg",
            "file_size": 2048000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/blackboard.jpg",
        }
        create_response = client.post(
            "/api/v1/photos", json=photo_data, headers=auth_headers
        )
        photo_id = create_response.json()["id"]

        # Mock OCR service
        mock_blackboard_data = BlackboardData(
            work_name="取得テスト工事", work_type="基礎工", station="200"
        )

        with patch("app.routers.ocr.OCRService") as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.extract_text_from_image.return_value = [
                {"text": "取得テスト工事", "confidence": 92.0}
            ]
            mock_ocr.parse_blackboard_text.return_value = mock_blackboard_data
            mock_ocr_class.return_value = mock_ocr

            # OCR処理実行
            client.post(f"/api/v1/photos/{photo_id}/process-ocr", headers=auth_headers)

            # OCR結果を取得
            response = client.get(
                f"/api/v1/photos/{photo_id}/ocr-result", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["photo_id"] == photo_id
            assert data["work_name"] == "取得テスト工事"
            assert data["work_type"] == "基礎工"

    def test_process_ocr_nonexistent_photo(self, client, auth_headers):
        """存在しない写真のOCR処理テスト"""
        response = client.post("/api/v1/photos/99999/process-ocr", headers=auth_headers)
        assert response.status_code == 404

    def test_get_ocr_result_not_processed(self, client, auth_headers):
        """OCR未処理の写真の結果取得テスト"""
        # 写真を作成（OCR処理なし）
        photo_data = {
            "file_name": "no_ocr.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/no_ocr.jpg",
        }
        create_response = client.post(
            "/api/v1/photos", json=photo_data, headers=auth_headers
        )
        photo_id = create_response.json()["id"]

        # OCR結果を取得（未処理）
        response = client.get(
            f"/api/v1/photos/{photo_id}/ocr-result", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == photo_id
        assert data["status"] == "not_processed"
        assert data.get("work_name") is None

    def test_unauthenticated_ocr_access(self, client):
        """認証なしOCRアクセスは拒否される"""
        # 認証なしでOCR処理トリガー
        response = client.post("/api/v1/photos/1/process-ocr")
        assert response.status_code == 403

        # 認証なしでOCR結果取得
        response = client.get("/api/v1/photos/1/ocr-result")
        assert response.status_code == 403
