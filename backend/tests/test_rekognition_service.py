"""
Amazon Rekognition サービスのテスト
"""

import pytest
from unittest.mock import Mock, patch
from app.services.rekognition_service import RekognitionService, ImageLabel


class TestRekognitionService:
    """RekognitionService のテスト"""

    @pytest.fixture
    @patch("boto3.client")
    def rekognition_service(self, mock_boto_client):
        """RekognitionServiceインスタンス"""
        mock_boto_client.return_value = Mock()
        return RekognitionService(confidence_threshold=80.0)

    @patch("boto3.client")
    def test_initialization(self, mock_boto_client):
        """初期化テスト"""
        mock_boto_client.return_value = Mock()
        service = RekognitionService(confidence_threshold=80.0)
        assert service.confidence_threshold == 80.0
        assert service.rekognition is not None

    @patch("boto3.client")
    def test_detect_labels_from_image_success(self, mock_boto_client):
        """画像からラベル検出成功テスト"""
        # モックレスポンス
        mock_rekognition = Mock()
        mock_rekognition.detect_labels.return_value = {
            "Labels": [
                {
                    "Name": "Construction",
                    "Confidence": 95.5,
                    "Parents": [],
                    "Instances": [],
                },
                {
                    "Name": "Worker",
                    "Confidence": 88.3,
                    "Parents": [{"Name": "Person"}],
                    "Instances": [{"BoundingBox": {}}],
                },
                {
                    "Name": "Helmet",
                    "Confidence": 92.1,
                    "Parents": [{"Name": "Safety Equipment"}],
                    "Instances": [],
                },
                {
                    "Name": "Building",
                    "Confidence": 75.0,  # 閾値以下
                    "Parents": [],
                    "Instances": [],
                },
            ]
        }
        mock_boto_client.return_value = mock_rekognition

        service = RekognitionService(confidence_threshold=80.0)
        labels = service.detect_labels_from_image(
            s3_bucket="test-bucket", s3_key="test.jpg"
        )

        # boto3呼び出し確認
        mock_rekognition.detect_labels.assert_called_once_with(
            Image={"S3Object": {"Bucket": "test-bucket", "Name": "test.jpg"}},
            MaxLabels=50,
            MinConfidence=80.0,
        )

        # フィルタリング確認（閾値80.0以上のみ）
        assert len(labels) == 3
        assert labels[0]["Name"] == "Construction"
        assert labels[0]["Confidence"] == 95.5
        assert labels[1]["Name"] == "Worker"
        assert labels[2]["Name"] == "Helmet"

    @patch("boto3.client")
    def test_detect_labels_empty_result(self, mock_boto_client):
        """ラベル検出結果が空の場合"""
        mock_rekognition = Mock()
        mock_rekognition.detect_labels.return_value = {"Labels": []}
        mock_boto_client.return_value = mock_rekognition

        service = RekognitionService()
        labels = service.detect_labels_from_image(
            s3_bucket="test-bucket", s3_key="empty.jpg"
        )

        assert labels == []

    def test_categorize_construction_labels(self, rekognition_service):
        """建設関連ラベルのカテゴリ分類テスト"""
        labels = [
            {"Name": "Excavator", "Confidence": 95.0},
            {"Name": "Construction Site", "Confidence": 90.0},
            {"Name": "Worker", "Confidence": 88.0},
            {"Name": "Helmet", "Confidence": 92.0},
            {"Name": "Safety Vest", "Confidence": 85.0},
            {"Name": "Concrete", "Confidence": 87.0},
            {"Name": "Rebar", "Confidence": 83.0},
            {"Name": "Tree", "Confidence": 80.0},  # 建設関連外
        ]

        categorized = rekognition_service.categorize_construction_labels(labels)

        # 建設機械
        assert "Excavator" in categorized["equipment"]

        # 作業員・安全
        assert "Worker" in categorized["people"]
        assert "Helmet" in categorized["safety"]
        assert "Safety Vest" in categorized["safety"]

        # 資材
        assert "Concrete" in categorized["materials"]
        assert "Rebar" in categorized["materials"]

        # シーン
        assert "Construction Site" in categorized["scene"]

        # その他
        assert "Tree" in categorized["other"]

    def test_filter_construction_related_labels(self, rekognition_service):
        """建設関連ラベルのフィルタリングテスト"""
        labels = [
            {"Name": "Construction", "Confidence": 95.0},
            {"Name": "Car", "Confidence": 90.0},  # 非建設関連
            {"Name": "Worker", "Confidence": 88.0},
            {"Name": "Sky", "Confidence": 85.0},  # 非建設関連
            {"Name": "Helmet", "Confidence": 92.0},
        ]

        filtered = rekognition_service.filter_construction_related(labels)

        # 建設関連のみ抽出
        assert len(filtered) == 3
        names = [label["Name"] for label in filtered]
        assert "Construction" in names
        assert "Worker" in names
        assert "Helmet" in names
        assert "Car" not in names
        assert "Sky" not in names

    def test_create_image_label_summary(self, rekognition_service):
        """画像ラベルサマリー作成テスト"""
        labels = [
            {"Name": "Construction Site", "Confidence": 95.0},
            {"Name": "Excavator", "Confidence": 90.0},
            {"Name": "Worker", "Confidence": 88.0},
            {"Name": "Helmet", "Confidence": 92.0},
        ]

        summary = rekognition_service.create_image_label_summary(labels)

        assert summary["total_labels"] == 4
        assert summary["max_confidence"] == 95.0
        assert summary["avg_confidence"] == pytest.approx(
            (95.0 + 90.0 + 88.0 + 92.0) / 4, rel=1e-2
        )
        assert summary["top_labels"] == [
            "Construction Site",
            "Helmet",
            "Excavator",
            "Worker",
        ]
        assert summary["has_construction_content"] is True

    def test_create_image_label_summary_no_construction(self, rekognition_service):
        """建設関連なしの場合"""
        labels = [
            {"Name": "Tree", "Confidence": 85.0},
            {"Name": "Sky", "Confidence": 80.0},
        ]

        summary = rekognition_service.create_image_label_summary(labels)

        assert summary["has_construction_content"] is False
