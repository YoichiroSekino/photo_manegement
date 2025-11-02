"""
PHOTO.XML生成サービスのテスト
"""

import pytest
from datetime import datetime
import xml.etree.ElementTree as ET

from app.services.photo_xml_generator import PhotoXMLGenerator


class TestPhotoXMLGenerator:
    """PHOTO.XMLジェネレーターテストクラス"""

    @pytest.fixture
    def xml_generator(self):
        """XMLジェネレーターのフィクスチャ"""
        return PhotoXMLGenerator()

    @pytest.fixture
    def photo_data_minimal(self):
        """最小限の写真データ"""
        return {
            "id": 1,
            "file_name": "P0000001.JPG",
            "title": "着手前全景",
            "shooting_date": "2024-03-15",
            "major_category": "工事",
            "photo_type": "着手前及び完成写真",
        }

    @pytest.fixture
    def photo_data_full(self):
        """完全な写真データ"""
        return {
            "id": 1,
            "file_name": "P0000001.JPG",
            "title": "基礎工_No.15+20.5_配筋状況_20240315",
            "shooting_date": "2024-03-15",
            "major_category": "工事",
            "photo_type": "施工状況写真",
            "work_type": "基礎工",
            "work_kind": "配筋工",
            "work_detail": "鉄筋組立",
            "photo_metadata": {
                "ocr_result": {
                    "station": "No.15+20.5",
                    "design_dimension": 500,
                    "actual_dimension": 498,
                    "inspector": "山田太郎",
                }
            },
        }

    def test_initialization(self, xml_generator):
        """初期化テスト"""
        assert xml_generator is not None
        assert hasattr(xml_generator, "generate_xml")
        assert hasattr(xml_generator, "validate_photo_data")

    def test_generate_xml_minimal(self, xml_generator, photo_data_minimal):
        """最小限のデータでXML生成テスト"""
        photos = [photo_data_minimal]
        xml_string = xml_generator.generate_xml(photos)

        assert isinstance(xml_string, str)
        assert '<?xml version="1.0" encoding="Shift_JIS"?>' in xml_string
        assert "<!DOCTYPE photodata SYSTEM" in xml_string
        assert '<photodata DTD_version="05">' in xml_string
        assert "<基礎情報>" in xml_string
        assert "<写真情報>" in xml_string

    def test_generate_xml_structure(self, xml_generator, photo_data_minimal):
        """XML構造テスト"""
        photos = [photo_data_minimal]
        xml_string = xml_generator.generate_xml(photos)

        # XMLパース（UTF-8でパース）
        # XML宣言とDOCTYPEを除外してパース
        xml_body = xml_string.split("\n", 2)[-1]  # 最初の2行（宣言とDOCTYPE）を除外
        root = ET.fromstring(xml_body)

        # ルート要素確認
        assert root.tag == "photodata"
        assert root.get("DTD_version") == "05"

        # 基礎情報確認
        basic_info = root.find("基礎情報")
        assert basic_info is not None

        folder_name = basic_info.find("写真フォルダ名")
        assert folder_name is not None
        assert folder_name.text == "PHOTO/PIC"

        standard = basic_info.find("適用要領基準")
        assert standard is not None
        assert standard.text == "土木202303-01"

    def test_generate_xml_photo_info(self, xml_generator, photo_data_minimal):
        """写真情報セクションテスト"""
        photos = [photo_data_minimal]
        xml_string = xml_generator.generate_xml(photos)

        xml_body = xml_string.split("\n", 2)[-1]
        root = ET.fromstring(xml_body)
        photo_info = root.find("写真情報")
        assert photo_info is not None

        # 写真ファイル情報
        file_info = photo_info.find("写真ファイル情報")
        assert file_info is not None

        serial = file_info.find("シリアル番号")
        assert serial is not None
        assert serial.text == "0000001"

        filename = file_info.find("写真ファイル名")
        assert filename is not None
        assert filename.text == "P0000001.JPG"

    def test_generate_xml_full_data(self, xml_generator, photo_data_full):
        """完全なデータでXML生成テスト"""
        photos = [photo_data_full]
        xml_string = xml_generator.generate_xml(photos)

        xml_body = xml_string.split("\n", 2)[-1]
        root = ET.fromstring(xml_body)
        photo_info = root.find("写真情報")

        # 撮影工種区分
        work_category = photo_info.find("撮影工種区分")
        assert work_category is not None

        work_type = work_category.find("工種")
        assert work_type is not None
        assert work_type.text == "基礎工"

        # 撮影情報
        shooting_info = photo_info.find("撮影情報")
        assert shooting_info is not None

        shooting_date = shooting_info.find("撮影年月日")
        assert shooting_date is not None
        assert shooting_date.text == "2024-03-15"

    def test_generate_xml_multiple_photos(self, xml_generator, photo_data_minimal):
        """複数写真のXML生成テスト"""
        photos = [
            {**photo_data_minimal, "id": 1, "file_name": "P0000001.JPG"},
            {**photo_data_minimal, "id": 2, "file_name": "P0000002.JPG"},
            {**photo_data_minimal, "id": 3, "file_name": "P0000003.JPG"},
        ]

        xml_string = xml_generator.generate_xml(photos)
        xml_body = xml_string.split("\n", 2)[-1]
        root = ET.fromstring(xml_body)

        # 写真情報が3つ存在することを確認
        photo_infos = root.findall("写真情報")
        assert len(photo_infos) == 3

    def test_validate_photo_data_valid(self, xml_generator, photo_data_full):
        """写真データバリデーション（正常）テスト"""
        errors = xml_generator.validate_photo_data(photo_data_full)
        assert isinstance(errors, list)
        # 完全なデータなのでエラーなし
        assert len(errors) == 0

    def test_validate_photo_data_missing_required(self, xml_generator):
        """必須項目不足のバリデーションテスト"""
        invalid_data = {
            "id": 1,
            "file_name": "P0000001.JPG",
            # title, shooting_date, major_category などが欠落
        }

        errors = xml_generator.validate_photo_data(invalid_data)
        assert len(errors) > 0
        # 必須項目のエラーが含まれる
        assert any("title" in error.lower() for error in errors)

    def test_format_serial_number(self, xml_generator):
        """シリアル番号フォーマットテスト"""
        # 7桁の連番形式
        assert xml_generator.format_serial_number(1) == "0000001"
        assert xml_generator.format_serial_number(123) == "0000123"
        assert xml_generator.format_serial_number(9999999) == "9999999"

    def test_format_date_ccyymmdd(self, xml_generator):
        """日付フォーマット（CCYY-MM-DD）テスト"""
        # 様々な入力形式
        assert xml_generator.format_date_ccyymmdd("2024-03-15") == "2024-03-15"
        assert xml_generator.format_date_ccyymmdd("20240315") == "2024-03-15"
        assert xml_generator.format_date_ccyymmdd("2024/03/15") == "2024-03-15"

    def test_validate_filename_format(self, xml_generator):
        """ファイル名形式バリデーションテスト"""
        # 正常なファイル名
        assert xml_generator.validate_filename("P0000001.JPG") == True
        assert xml_generator.validate_filename("P1234567.JPG") == True

        # 異常なファイル名
        assert xml_generator.validate_filename("photo001.jpg") == False
        assert xml_generator.validate_filename("P123.JPG") == False
        assert xml_generator.validate_filename("D0000001.JPG") == False

    def test_validate_title_length(self, xml_generator):
        """タイトル長さバリデーションテスト"""
        # 127文字以内（正常）
        valid_title = "基礎工_配筋検査"
        assert xml_generator.validate_title(valid_title) == True

        # 127文字超過（異常）
        invalid_title = "あ" * 128
        assert xml_generator.validate_title(invalid_title) == False

    def test_check_work_category_rules(self, xml_generator):
        """工種区分記入可否ルールテスト"""
        # 着手前及び完成写真：工種記入不要
        assert xml_generator.check_work_category_required("着手前及び完成写真") == False

        # 品質管理写真：工種記入必須
        assert xml_generator.check_work_category_required("品質管理写真") == True

        # 施工状況写真：工種記入可能
        result = xml_generator.check_work_category_required("施工状況写真")
        assert result in [True, False, "optional"]

    def test_escape_xml_special_chars(self, xml_generator):
        """XML特殊文字エスケープテスト"""
        # 特殊文字を含むテキスト
        text_with_special = 'テスト<>&"テスト'
        escaped = xml_generator.escape_xml_special_chars(text_with_special)

        assert "<" not in escaped
        assert ">" not in escaped
        assert "&" not in escaped or "&amp;" in escaped
        assert '"' not in escaped or "&quot;" in escaped

    def test_generate_xml_encoding(self, xml_generator, photo_data_minimal):
        """XMLエンコーディングテスト"""
        photos = [photo_data_minimal]
        xml_string = xml_generator.generate_xml(photos)

        # Shift_JISでエンコード可能か確認
        try:
            xml_bytes = xml_string.encode("shift_jis")
            assert len(xml_bytes) > 0
        except UnicodeEncodeError:
            pytest.fail("Shift_JISエンコードに失敗しました")

    def test_pretty_print_xml(self, xml_generator, photo_data_minimal):
        """XML整形（pretty print）テスト"""
        photos = [photo_data_minimal]
        xml_string = xml_generator.generate_xml(photos, pretty_print=True)

        # インデントが含まれているか確認
        assert "\n" in xml_string
        assert "  " in xml_string or "\t" in xml_string
