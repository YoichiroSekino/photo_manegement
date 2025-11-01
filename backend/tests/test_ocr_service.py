"""
OCRサービスのテスト
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ocr_service import OCRService, BlackboardData


def test_extract_text_from_image():
    """画像からテキストを抽出するテスト"""
    # Mock Textract response
    mock_response = {
        "Blocks": [
            {
                "BlockType": "LINE",
                "Text": "○○工事",
                "Confidence": 95.5,
            },
            {
                "BlockType": "LINE",
                "Text": "工種：土工",
                "Confidence": 92.3,
            },
            {
                "BlockType": "LINE",
                "Text": "測点No.100+5.0",
                "Confidence": 88.7,
            },
        ]
    }

    with patch("boto3.client") as mock_boto:
        mock_textract = Mock()
        mock_textract.detect_document_text.return_value = mock_response
        mock_boto.return_value = mock_textract

        service = OCRService()
        result = service.extract_text_from_image(
            s3_bucket="test-bucket", s3_key="test-key.jpg"
        )

        assert len(result) == 3
        assert result[0]["text"] == "○○工事"
        assert result[0]["confidence"] == 95.5
        assert result[1]["text"] == "工種：土工"
        assert result[2]["text"] == "測点No.100+5.0"


def test_parse_blackboard_text():
    """黒板テキストから工事情報を抽出するテスト"""
    text_blocks = [
        {"text": "〇〇〇〇工事", "confidence": 95.0},
        {"text": "工種：土工", "confidence": 92.0},
        {"text": "種別：掘削工", "confidence": 90.0},
        {"text": "測点No.100+5.0", "confidence": 88.0},
        {"text": "撮影日：2024-03-15", "confidence": 93.0},
        {"text": "設計：500mm 実測：498mm", "confidence": 85.0},
        {"text": "立会者：山田太郎", "confidence": 91.0},
    ]

    service = OCRService()
    result = service.parse_blackboard_text(text_blocks)

    assert result.work_name == "〇〇〇〇工事"
    assert result.work_type == "土工"
    assert result.work_kind == "掘削工"
    assert result.station == "100+5.0"
    assert result.shooting_date == "2024-03-15"
    assert result.design_dimension == 500
    assert result.actual_dimension == 498
    assert result.inspector == "山田太郎"


def test_extract_station_number():
    """測点番号抽出のテスト"""
    service = OCRService()

    # パターン1: 基本形式
    assert service.extract_station_number("測点No.100+5.0") == "100+5.0"

    # パターン2: スペースあり
    assert service.extract_station_number("測点 No. 200 + 10.5") == "200+10.5"

    # パターン3: マイナス
    assert service.extract_station_number("No.50-3.5") == "50-3.5"

    # パターン4: 測点なし
    assert service.extract_station_number("工種：土工") is None


def test_extract_dimensions():
    """寸法情報抽出のテスト"""
    service = OCRService()

    # パターン1: 設計と実測両方
    result = service.extract_dimensions("設計：500mm 実測：498mm")
    assert result["design"] == 500
    assert result["actual"] == 498

    # パターン2: 設計のみ
    result = service.extract_dimensions("設計寸法: 1200 mm")
    assert result["design"] == 1200
    assert result.get("actual") is None

    # パターン3: 実測のみ
    result = service.extract_dimensions("実測: 350mm")
    assert result.get("design") is None
    assert result["actual"] == 350

    # パターン4: 寸法なし
    result = service.extract_dimensions("工種：土工")
    assert result == {}


def test_extract_date():
    """撮影日抽出のテスト"""
    service = OCRService()

    # パターン1: YYYY-MM-DD形式
    assert service.extract_date("撮影日：2024-03-15") == "2024-03-15"

    # パターン2: YYYY/MM/DD形式
    assert service.extract_date("撮影日:2024/03/15") == "2024-03-15"

    # パターン3: 和暦
    assert service.extract_date("令和6年3月15日") == "2024-03-15"

    # パターン4: 日付なし
    assert service.extract_date("工種：土工") is None


def test_parse_blackboard_with_partial_data():
    """一部のデータのみの黒板テキスト解析テスト"""
    text_blocks = [
        {"text": "工事名不明", "confidence": 50.0},  # 低信頼度
        {"text": "測点No.200", "confidence": 90.0},
    ]

    service = OCRService()
    result = service.parse_blackboard_text(text_blocks)

    # 低信頼度のデータは無視される
    assert result.work_name is None
    assert result.station == "200"
    assert result.work_type is None


def test_confidence_threshold():
    """信頼度閾値のテスト"""
    text_blocks = [
        {"text": "工種：土工", "confidence": 95.0},  # 高信頼度
        {"text": "不明なテキスト", "confidence": 60.0},  # 低信頼度（デフォルト閾値70未満）
    ]

    service = OCRService(confidence_threshold=70.0)
    result = service.parse_blackboard_text(text_blocks)

    # 信頼度70以上のみ採用
    assert result.work_type == "土工"
