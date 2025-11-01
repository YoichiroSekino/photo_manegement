"""
Amazon Rekognition API エンドポイントのテスト
"""

import pytest
from unittest.mock import Mock, patch

from app.database.models import Photo


class TestRekognitionAPI:
    """Rekognition API エンドポイントのテスト"""

    @pytest.fixture
    def sample_photo(self, db):
        """テスト用写真データ作成"""
        photo = Photo(
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
    def test_classify_image_success(self, mock_boto_client, sample_photo, client):
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

        response = client.post(f"/api/v1/photos/{sample_photo}/classify")

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
    def test_classify_image_photo_not_found(self, mock_boto_client, client):
        """存在しない写真IDの場合"""
        mock_boto_client.return_value = Mock()

        response = client.post("/api/v1/photos/999/classify")

        assert response.status_code == 404
        assert "写真が見つかりません" in response.json()["detail"]

    @patch("app.services.rekognition_service.boto3.client")
    def test_classify_image_saves_to_database(
        self, mock_boto_client, sample_photo, client, db
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

        response = client.post(f"/api/v1/photos/{sample_photo}/classify")

        assert response.status_code == 200

        # データベース確認
        db.expire_all()  # セッションを更新
        photo = db.query(Photo).filter(Photo.id == sample_photo).first()
        assert photo is not None
        assert photo.photo_metadata is not None
        assert "rekognition_labels" in photo.photo_metadata
        assert len(photo.photo_metadata["rekognition_labels"]) == 1

    def test_get_classification_result_not_processed(self, sample_photo, client):
        """未処理写真の分類結果取得テスト"""
        response = client.get(f"/api/v1/photos/{sample_photo}/classification")

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == sample_photo
        assert data["status"] == "not_processed"
        assert data["labels"] == []

    @patch("app.services.rekognition_service.boto3.client")
    def test_get_classification_result_processed(
        self, mock_boto_client, sample_photo, client
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

        client.post(f"/api/v1/photos/{sample_photo}/classify")

        # 結果取得
        response = client.get(f"/api/v1/photos/{sample_photo}/classification")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert len(data["labels"]) == 1
        assert data["labels"][0]["name"] == "Worker"

    def test_get_classification_result_photo_not_found(self, client):
        """存在しない写真の分類結果取得テスト"""
        response = client.get("/api/v1/photos/999/classification")

        assert response.status_code == 404
        assert "写真が見つかりません" in response.json()["detail"]
