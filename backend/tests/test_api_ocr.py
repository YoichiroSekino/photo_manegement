"""
OCR処理APIエンドポイントのテスト
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ocr_service import BlackboardData


def test_process_ocr(client, db):
    """OCR処理トリガーAPIのテスト"""
    # まず写真を作成
    photo_data = {
        "file_name": "blackboard.jpg",
        "file_size": 2048000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/blackboard.jpg",
    }
    create_response = client.post("/api/v1/photos", json=photo_data)
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
        response = client.post(f"/api/v1/photos/{photo_id}/process-ocr")

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == photo_id
        assert data["status"] == "completed"
        assert data["blackboard_data"]["work_name"] == "テスト工事"
        assert data["blackboard_data"]["work_type"] == "土工"


def test_get_ocr_result(client, db):
    """OCR結果取得APIのテスト"""
    # 写真を作成してOCR処理
    photo_data = {
        "file_name": "blackboard.jpg",
        "file_size": 2048000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/blackboard.jpg",
    }
    create_response = client.post("/api/v1/photos", json=photo_data)
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
        client.post(f"/api/v1/photos/{photo_id}/process-ocr")

        # OCR結果を取得
        response = client.get(f"/api/v1/photos/{photo_id}/ocr-result")

        assert response.status_code == 200
        data = response.json()
        assert data["photo_id"] == photo_id
        assert data["work_name"] == "取得テスト工事"
        assert data["work_type"] == "基礎工"


def test_process_ocr_nonexistent_photo(client):
    """存在しない写真のOCR処理テスト"""
    response = client.post("/api/v1/photos/99999/process-ocr")
    assert response.status_code == 404


def test_get_ocr_result_not_processed(client, db):
    """OCR未処理の写真の結果取得テスト"""
    # 写真を作成（OCR処理なし）
    photo_data = {
        "file_name": "no_ocr.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/no_ocr.jpg",
    }
    create_response = client.post("/api/v1/photos", json=photo_data)
    photo_id = create_response.json()["id"]

    # OCR結果を取得（未処理）
    response = client.get(f"/api/v1/photos/{photo_id}/ocr-result")

    assert response.status_code == 200
    data = response.json()
    assert data["photo_id"] == photo_id
    assert data["status"] == "not_processed"
    assert data.get("work_name") is None
