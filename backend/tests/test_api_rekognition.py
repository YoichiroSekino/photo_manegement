"""
Amazon Rekognition API エンドポイントのテスト（マルチテナント対応）
"""

import pytest
from unittest.mock import Mock, patch

from app.database.models import Photo, Organization, User, Project
from app.auth.jwt_handler import create_tokens


class TestRekognitionAPI:
    """Rekognition API エンドポイントのテスト"""

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
    def test_project(self, db, test_org):
        """テスト用プロジェクト"""
        project = Project(
            name="Test Project",
            organization_id=test_org.id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダー"""
        tokens = create_tokens(test_user.id, test_user.email, test_user.organization_id)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @pytest.fixture
    def sample_photo(self, db, test_org, test_project):
        """テスト用写真データ作成"""
        photo = Photo(
            organization_id=test_org.id,
            project_id=test_project.id,
            file_name="test_construction.jpg",
            file_size=2048000,
            mime_type="image/jpeg",
            s3_key="photos/test_construction.jpg",
            title="建設現場写真",
            description="掘削作業中",
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo.id

    @patch("app.services.rekognition_service.boto3.client")
    def test_classify_image_success(
        self, mock_boto_client, sample_photo, client, auth_headers
    ):
        """画像分類成功テスト"""
        # モックRekognition
        mock_rekognition = Mock()
        mock_rekognition.detect_labels.return_value = {
            "Labels": [
                {"Name": "Construction", "Confidence": 95.5, "Parents": []},
                {"Name": "Excavator", "Confidence": 92.3, "Parents": []},
                {"Name": "Worker", "Confidence": 88.7, "Parents": [{"Name": "Person"}]},
                {"Name": "Helmet", "Confidence": 90.1, "Parents": []},
            ]
        }
        mock_boto_client.return_value = mock_rekognition

        response = client.post(
            f"/api/v1/photos/{sample_photo}/classify", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == sample_photo
        assert data["status"] == "completed"
        assert len(data["labels"]) == 4
        assert data["labels"][0]["name"] == "Construction"
        assert data["labels"][0]["confidence"] == 95.5

        # カテゴリ分類確認
        assert "equipment" in data["categorized_labels"]
        assert "Excavator" in data["categorized_labels"]["equipment"]
        assert "Worker" in data["categorized_labels"]["people"]

        # サマリー確認
        assert data["summary"]["total_labels"] == 4
        assert data["summary"]["has_construction_content"] is True

    @patch("app.services.rekognition_service.boto3.client")
    def test_classify_image_photo_not_found(
        self, mock_boto_client, client, auth_headers
    ):
        """存在しない写真IDの場合"""
        mock_boto_client.return_value = Mock()

        response = client.post("/api/v1/photos/999/classify", headers=auth_headers)

        assert response.status_code == 404
        assert "写真が見つかりません" in response.json()["detail"]

    @patch("app.services.rekognition_service.boto3.client")
    def test_classify_image_saves_to_database(
        self, mock_boto_client, sample_photo, client, auth_headers, db
    ):
        """画像分類結果がデータベースに保存されるテスト"""
        # モックRekognition
        mock_rekognition = Mock()
        mock_rekognition.detect_labels.return_value = {
            "Labels": [
                {"Name": "Construction Site", "Confidence": 94.0, "Parents": []},
            ]
        }
        mock_boto_client.return_value = mock_rekognition

        response = client.post(
            f"/api/v1/photos/{sample_photo}/classify", headers=auth_headers
        )

        assert response.status_code == 200

        # データベース確認
        db.expire_all()  # セッションを更新
        photo = db.query(Photo).filter(Photo.id == sample_photo).first()
        assert photo is not None
        assert photo.photo_metadata is not None
        assert "rekognition_labels" in photo.photo_metadata
        assert len(photo.photo_metadata["rekognition_labels"]) == 1

    def test_get_classification_result_not_processed(
        self, sample_photo, client, auth_headers
    ):
        """未処理写真の分類結果取得テスト"""
        response = client.get(
            f"/api/v1/photos/{sample_photo}/classification", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == sample_photo
        assert data["status"] == "not_processed"
        assert data["labels"] == []

    @patch("app.services.rekognition_service.boto3.client")
    def test_get_classification_result_processed(
        self, mock_boto_client, sample_photo, client, auth_headers
    ):
        """処理済み写真の分類結果取得テスト"""
        # まず分類実行
        mock_rekognition = Mock()
        mock_rekognition.detect_labels.return_value = {
            "Labels": [
                {"Name": "Worker", "Confidence": 88.0, "Parents": []},
            ]
        }
        mock_boto_client.return_value = mock_rekognition

        client.post(f"/api/v1/photos/{sample_photo}/classify", headers=auth_headers)

        # 結果取得
        response = client.get(
            f"/api/v1/photos/{sample_photo}/classification", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert len(data["labels"]) == 1
        assert data["labels"][0]["name"] == "Worker"

    def test_get_classification_result_photo_not_found(self, client, auth_headers):
        """存在しない写真の分類結果取得テスト"""
        response = client.get("/api/v1/photos/999/classification", headers=auth_headers)

        assert response.status_code == 404
        assert "写真が見つかりません" in response.json()["detail"]

    def test_unauthenticated_rekognition_access(self, client):
        """認証なしRekognitionアクセスは拒否される"""
        # 認証なしで画像分類
        response = client.post("/api/v1/photos/1/classify")
        assert response.status_code == 403

        # 認証なしで分類結果取得
        response = client.get("/api/v1/photos/1/classification")
        assert response.status_code == 403
