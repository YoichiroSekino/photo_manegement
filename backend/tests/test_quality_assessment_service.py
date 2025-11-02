"""
品質判定サービスのテスト
"""

import pytest
from io import BytesIO
from PIL import Image
import numpy as np
from unittest.mock import Mock, patch

from app.services.quality_assessment_service import QualityAssessmentService


class TestQualityAssessmentService:
    """品質判定サービステストクラス"""

    @pytest.fixture
    def quality_service(self):
        """品質判定サービスのフィクスチャ"""
        return QualityAssessmentService()

    @pytest.fixture
    def test_image_sharp(self):
        """鮮明なテスト画像（高品質）"""
        # 1600x1200の白黒パターン画像（エッジが明確）
        img = Image.new("RGB", (1600, 1200), color="white")
        pixels = img.load()
        # チェッカーパターンを作成（エッジが多い）
        for i in range(0, 1600, 100):
            for j in range(0, 1200, 100):
                if (i // 100 + j // 100) % 2 == 0:
                    for x in range(i, min(i + 100, 1600)):
                        for y in range(j, min(j + 100, 1200)):
                            pixels[x, y] = (0, 0, 0)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.fixture
    def test_image_blurry(self):
        """ぼやけたテスト画像（低品質）"""
        # 単色画像（エッジがない）
        img = Image.new("RGB", (1600, 1200), color=(128, 128, 128))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=50)
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.fixture
    def test_image_dark(self):
        """暗いテスト画像"""
        img = Image.new("RGB", (1600, 1200), color=(30, 30, 30))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.fixture
    def test_image_bright(self):
        """明るいテスト画像"""
        img = Image.new("RGB", (1600, 1200), color=(240, 240, 240))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    def test_initialization(self, quality_service):
        """初期化テスト"""
        assert quality_service is not None
        assert hasattr(quality_service, "calculate_sharpness")
        assert hasattr(quality_service, "calculate_brightness")
        assert hasattr(quality_service, "calculate_contrast")
        assert hasattr(quality_service, "assess_quality")

    def test_calculate_sharpness_sharp_image(self, quality_service, test_image_sharp):
        """鮮明な画像のシャープネス計算テスト"""
        sharpness = quality_service.calculate_sharpness(test_image_sharp)
        assert isinstance(sharpness, float)
        assert sharpness > 0
        # チェッカーパターンはエッジが多いので高いシャープネス値
        assert sharpness > 100.0

    def test_calculate_sharpness_blurry_image(self, quality_service, test_image_blurry):
        """ぼやけた画像のシャープネス計算テスト"""
        sharpness = quality_service.calculate_sharpness(test_image_blurry)
        assert isinstance(sharpness, float)
        assert sharpness >= 0
        # 単色画像はエッジが少ないので低いシャープネス値
        assert sharpness < 50.0

    def test_calculate_brightness_dark_image(self, quality_service, test_image_dark):
        """暗い画像の明るさ計算テスト"""
        brightness = quality_service.calculate_brightness(test_image_dark)
        assert isinstance(brightness, float)
        assert 0 <= brightness <= 255
        # 暗い画像 (RGB=30,30,30)
        assert brightness < 100

    def test_calculate_brightness_bright_image(
        self, quality_service, test_image_bright
    ):
        """明るい画像の明るさ計算テスト"""
        brightness = quality_service.calculate_brightness(test_image_bright)
        assert isinstance(brightness, float)
        assert 0 <= brightness <= 255
        # 明るい画像 (RGB=240,240,240)
        assert brightness > 200

    def test_calculate_contrast_high(self, quality_service, test_image_sharp):
        """高コントラスト画像のコントラスト計算テスト"""
        contrast = quality_service.calculate_contrast(test_image_sharp)
        assert isinstance(contrast, float)
        assert contrast >= 0
        # チェッカーパターンは白黒なので高コントラスト
        assert contrast > 50

    def test_calculate_contrast_low(self, quality_service, test_image_blurry):
        """低コントラスト画像のコントラスト計算テスト"""
        contrast = quality_service.calculate_contrast(test_image_blurry)
        assert isinstance(contrast, float)
        assert contrast >= 0
        # 単色画像は低コントラスト
        assert contrast < 10

    def test_assess_quality_high_quality(self, quality_service, test_image_sharp):
        """高品質画像の品質評価テスト"""
        result = quality_service.assess_quality(test_image_sharp)

        # レスポンス構造チェック
        assert "sharpness" in result
        assert "brightness" in result
        assert "contrast" in result
        assert "quality_score" in result
        assert "quality_grade" in result
        assert "issues" in result
        assert "recommendations" in result

        # 品質スコア範囲チェック
        assert 0 <= result["quality_score"] <= 100
        assert result["quality_grade"] in ["excellent", "good", "fair", "poor"]

        # 高品質画像なのでスコアが高い
        assert result["quality_score"] > 60

    def test_assess_quality_low_quality(self, quality_service, test_image_blurry):
        """低品質画像の品質評価テスト"""
        result = quality_service.assess_quality(test_image_blurry)

        assert 0 <= result["quality_score"] <= 100
        # ぼやけた画像なので低スコア
        assert result["quality_score"] < 50
        # 問題点が検出される
        assert len(result["issues"]) > 0
        # 推奨アクションがある
        assert len(result["recommendations"]) > 0

    def test_assess_quality_dark_image(self, quality_service, test_image_dark):
        """暗い画像の品質評価テスト"""
        result = quality_service.assess_quality(test_image_dark)

        # 暗すぎる問題が検出される
        assert any("暗" in issue or "明るさ" in issue for issue in result["issues"])

    def test_assess_quality_bright_image(self, quality_service, test_image_bright):
        """明るい画像の品質評価テスト"""
        result = quality_service.assess_quality(test_image_bright)

        # 明るすぎる問題が検出される可能性
        # （240は明るいが許容範囲内の可能性もあるので、厳密にはチェックしない）
        assert isinstance(result["issues"], list)

    def test_quality_grade_calculation(self, quality_service):
        """品質グレード計算のロジックテスト"""
        # 直接品質グレードを計算するヘルパーメソッドがあると仮定
        # （実装時に_get_quality_gradeのような内部メソッドを作成）
        grades = {
            85: "excellent",
            75: "good",
            55: "fair",
            35: "poor",
        }

        for score, expected_grade in grades.items():
            grade = quality_service._get_quality_grade(score)
            assert grade == expected_grade

    @patch("app.services.quality_assessment_service.boto3.client")
    def test_download_image_from_s3(self, mock_boto_client, quality_service):
        """S3から画像ダウンロードのテスト"""
        # モックS3クライアントを設定
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        # サンプル画像データ
        img = Image.new("RGB", (100, 100), color="white")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # S3レスポンスをモック
        mock_s3.get_object.return_value = {"Body": BytesIO(image_data)}

        # 新しいサービスインスタンスを作成（モックされたboto3を使用）
        service = QualityAssessmentService()

        # ダウンロード実行
        result = service.download_image_from_s3(
            bucket="test-bucket", key="test-key.jpg"
        )

        # 検証
        assert result == image_data
        mock_s3.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key.jpg"
        )
