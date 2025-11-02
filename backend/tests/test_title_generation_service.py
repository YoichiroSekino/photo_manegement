"""
タイトル自動生成サービスのテスト
"""

import pytest
from datetime import datetime

from app.services.title_generation_service import TitleGenerationService


class TestTitleGenerationService:
    """タイトル自動生成サービステストクラス"""

    @pytest.fixture
    def title_service(self):
        """タイトル生成サービスのフィクスチャ"""
        return TitleGenerationService()

    @pytest.fixture
    def ocr_data_full(self):
        """完全なOCRデータ"""
        return {
            "work_type": "基礎工",
            "work_kind": "配筋工",
            "station": "No.15+20.5",
            "shooting_date": "2024-03-15",
        }

    @pytest.fixture
    def ocr_data_partial(self):
        """部分的なOCRデータ"""
        return {
            "work_type": "土工",
            "shooting_date": "2024-03-20",
        }

    @pytest.fixture
    def classification_data(self):
        """分類データ"""
        return {
            "categorized_labels": {
                "equipment": ["excavator", "crane"],
                "people": ["worker"],
                "safety": ["helmet", "safety vest"],
                "materials": ["concrete"],
                "scene": ["construction"],
            }
        }

    def test_initialization(self, title_service):
        """初期化テスト"""
        assert title_service is not None
        assert hasattr(title_service, "generate_title")
        assert hasattr(title_service, "format_station")
        assert hasattr(title_service, "format_date")

    def test_generate_title_with_full_ocr_data(
        self, title_service, ocr_data_full, classification_data
    ):
        """完全なOCRデータからタイトル生成テスト"""
        title = title_service.generate_title(
            ocr_data=ocr_data_full, classification_data=classification_data
        )

        assert isinstance(title, str)
        assert len(title) > 0
        # フォーマット: [工種]_[測点]_[撮影対象]_[撮影日]
        assert "基礎工" in title
        assert "No.15+20.5" in title
        assert "20240315" in title

    def test_generate_title_with_partial_ocr_data(
        self, title_service, ocr_data_partial, classification_data
    ):
        """部分的なOCRデータからタイトル生成テスト"""
        title = title_service.generate_title(
            ocr_data=ocr_data_partial, classification_data=classification_data
        )

        assert isinstance(title, str)
        assert "土工" in title
        assert "20240320" in title

    def test_generate_title_with_no_ocr_data(
        self, title_service, classification_data
    ):
        """OCRデータなしでタイトル生成テスト"""
        title = title_service.generate_title(
            ocr_data={}, classification_data=classification_data
        )

        assert isinstance(title, str)
        # 分類データから撮影対象を推定
        assert len(title) > 0

    def test_generate_title_with_no_classification_data(
        self, title_service, ocr_data_full
    ):
        """分類データなしでタイトル生成テスト"""
        title = title_service.generate_title(
            ocr_data=ocr_data_full, classification_data={}
        )

        assert isinstance(title, str)
        assert "基礎工" in title
        assert "No.15+20.5" in title

    def test_generate_title_with_no_data(self, title_service):
        """データなしでタイトル生成テスト"""
        title = title_service.generate_title(ocr_data={}, classification_data={})

        assert isinstance(title, str)
        # デフォルトタイトルが生成される
        assert "工事写真" in title or "photo" in title.lower()

    def test_format_station_valid(self, title_service):
        """測点フォーマットテスト（正常）"""
        # 様々な測点フォーマット
        test_cases = {
            "No.15+20.5": "No.15+20.5",
            "15+20.5": "No.15+20.5",
            "No.100": "No.100",
            "100": "No.100",
            "測点No.15": "No.15",
        }

        for input_station, expected in test_cases.items():
            result = title_service.format_station(input_station)
            assert result == expected

    def test_format_station_invalid(self, title_service):
        """測点フォーマットテスト（無効）"""
        result = title_service.format_station("")
        assert result == ""

        result = title_service.format_station(None)
        assert result == ""

    def test_format_date_valid(self, title_service):
        """日付フォーマットテスト（正常）"""
        # 様々な日付フォーマット
        test_cases = {
            "2024-03-15": "20240315",
            "2024/03/15": "20240315",
            "20240315": "20240315",
            "2024.03.15": "20240315",
        }

        for input_date, expected in test_cases.items():
            result = title_service.format_date(input_date)
            assert result == expected

    def test_format_date_invalid(self, title_service):
        """日付フォーマットテスト（無効）"""
        result = title_service.format_date("")
        # 空の場合は今日の日付
        assert len(result) == 8  # YYYYMMDD形式

        result = title_service.format_date(None)
        assert len(result) == 8

        result = title_service.format_date("invalid-date")
        # 無効な日付の場合は今日の日付
        assert len(result) == 8

    def test_infer_subject_from_classification(self, title_service):
        """分類データから撮影対象を推定テスト"""
        classification_data = {
            "categorized_labels": {
                "equipment": ["excavator"],
                "people": ["worker"],
                "safety": ["helmet"],
            }
        }

        subject = title_service.infer_subject_from_classification(classification_data)
        assert isinstance(subject, str)
        assert len(subject) > 0
        # 重機、作業員、安全装備のいずれかが含まれる
        assert any(
            keyword in subject
            for keyword in ["重機", "掘削", "作業", "安全", "ヘルメット"]
        )

    def test_infer_subject_from_work_type(self, title_service):
        """工種から撮影対象を推定テスト"""
        test_cases = {
            "基礎工": "基礎",
            "土工": "土工",
            "配筋工": "配筋",
            "型枠工": "型枠",
        }

        for work_type, expected_keyword in test_cases.items():
            subject = title_service.infer_subject_from_work_type(work_type)
            assert expected_keyword in subject

    def test_validate_title_length(self, title_service):
        """タイトル長さバリデーションテスト"""
        # 127文字以内（デジタル写真管理情報基準）
        long_title = "あ" * 150
        validated = title_service.validate_title(long_title)
        assert len(validated) <= 127

    def test_validate_title_characters(self, title_service):
        """タイトル文字バリデーションテスト"""
        # 無効な文字を含むタイトル
        invalid_title = "基礎工<test>_No.15"
        validated = title_service.validate_title(invalid_title)
        # 無効な文字（<>など）が除去される
        assert "<" not in validated
        assert ">" not in validated

    def test_generate_title_format_consistency(
        self, title_service, ocr_data_full, classification_data
    ):
        """タイトルフォーマット一貫性テスト"""
        # 同じデータで複数回生成
        title1 = title_service.generate_title(
            ocr_data=ocr_data_full, classification_data=classification_data
        )
        title2 = title_service.generate_title(
            ocr_data=ocr_data_full, classification_data=classification_data
        )

        # 同じ入力からは同じタイトルが生成される
        assert title1 == title2

    def test_generate_title_with_metadata(
        self, title_service, ocr_data_full, classification_data
    ):
        """メタデータ付きタイトル生成テスト"""
        result = title_service.generate_title_with_metadata(
            ocr_data=ocr_data_full, classification_data=classification_data
        )

        assert "title" in result
        assert "work_type" in result
        assert "station" in result
        assert "subject" in result
        assert "date" in result
        assert "confidence" in result

        assert isinstance(result["title"], str)
        assert isinstance(result["confidence"], float)
        assert 0 <= result["confidence"] <= 100
