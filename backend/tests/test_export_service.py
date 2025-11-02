"""
エクスポートサービスのテスト
"""

import pytest
import os
import zipfile
from datetime import datetime
from pathlib import Path

from app.services.export_service import ExportService


class TestExportService:
    """エクスポートサービステストクラス"""

    @pytest.fixture
    def export_service(self):
        """エクスポートサービスのフィクスチャ"""
        return ExportService()

    @pytest.fixture
    def photo_data_minimal(self):
        """最小限の写真データ"""
        return {
            "id": 1,
            "file_name": "IMG_0001.JPG",
            "title": "着手前全景",
            "shooting_date": "2024-03-15",
            "major_category": "工事",
            "photo_type": "着手前及び完成写真",
        }

    @pytest.fixture
    def photo_data_list(self):
        """複数写真データ"""
        return [
            {
                "id": 1,
                "file_name": "IMG_0001.JPG",
                "title": "着手前全景",
                "shooting_date": "2024-03-15",
                "major_category": "工事",
            },
            {
                "id": 2,
                "file_name": "IMG_0002.JPG",
                "title": "配筋状況",
                "shooting_date": "2024-03-16",
                "major_category": "工事",
            },
            {
                "id": 3,
                "file_name": "IMG_0003.JPG",
                "title": "完成全景",
                "shooting_date": "2024-03-17",
                "major_category": "工事",
            },
        ]

    def test_initialization(self, export_service):
        """初期化テスト"""
        assert export_service is not None
        assert hasattr(export_service, "generate_serial_number")
        assert hasattr(export_service, "rename_photo_file")
        assert hasattr(export_service, "create_folder_structure")
        assert hasattr(export_service, "export_package")

    def test_generate_serial_number(self, export_service):
        """シリアル番号生成テスト"""
        # P0000001形式
        assert export_service.generate_serial_number(1) == "P0000001"
        assert export_service.generate_serial_number(123) == "P0000123"
        assert export_service.generate_serial_number(9999999) == "P9999999"

    def test_generate_serial_number_with_prefix(self, export_service):
        """プレフィックス付きシリアル番号生成テスト"""
        # Dプレフィックス（参考図）
        assert export_service.generate_serial_number(1, prefix="D") == "D0000001"
        assert export_service.generate_serial_number(10, prefix="D") == "D0000010"

    def test_rename_photo_file(self, export_service, photo_data_minimal):
        """ファイル名リネームテスト"""
        renamed = export_service.rename_photo_file(photo_data_minimal, 1)

        assert renamed["new_file_name"] == "P0000001.JPG"
        assert renamed["original_file_name"] == "IMG_0001.JPG"
        assert renamed["photo_id"] == 1
        assert renamed["serial_number"] == 1

    def test_rename_multiple_photos(self, export_service, photo_data_list):
        """複数写真リネームテスト"""
        renamed_list = export_service.rename_multiple_photos(photo_data_list)

        assert len(renamed_list) == 3
        assert renamed_list[0]["new_file_name"] == "P0000001.JPG"
        assert renamed_list[1]["new_file_name"] == "P0000002.JPG"
        assert renamed_list[2]["new_file_name"] == "P0000003.JPG"

    def test_check_filename_duplication(self, export_service, photo_data_list):
        """ファイル名重複チェックテスト"""
        # 重複なし
        duplicates = export_service.check_filename_duplication(photo_data_list)
        assert len(duplicates) == 0

        # 重複あり
        photo_data_list_dup = photo_data_list + [photo_data_list[0]]
        duplicates = export_service.check_filename_duplication(photo_data_list_dup)
        assert len(duplicates) > 0

    def test_create_folder_structure(self, export_service, tmp_path):
        """フォルダ構造作成テスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        # フォルダが作成されているか確認
        assert os.path.exists(folders["root"])
        assert os.path.exists(folders["pic"])
        assert os.path.exists(folders["dra"])

        # パス確認
        assert folders["root"] == str(export_dir / "PHOTO")
        assert folders["pic"] == str(export_dir / "PHOTO" / "PIC")
        assert folders["dra"] == str(export_dir / "PHOTO" / "DRA")

    def test_validate_folder_structure(self, export_service, tmp_path):
        """フォルダ構造バリデーションテスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        # バリデーション実行
        is_valid, errors = export_service.validate_folder_structure(folders["root"])

        # 初期状態では有効
        assert is_valid == True
        assert len(errors) == 0

    def test_get_dtd_template_path(self, export_service):
        """DTDテンプレートパス取得テスト"""
        dtd_path = export_service.get_dtd_template_path()
        assert dtd_path is not None
        assert "PHOTO05.DTD" in dtd_path

    def test_get_xsl_template_path(self, export_service):
        """XSLテンプレートパス取得テスト"""
        xsl_path = export_service.get_xsl_template_path()
        assert xsl_path is not None
        assert "PHOTO05.XSL" in xsl_path

    def test_copy_templates_to_folder(self, export_service, tmp_path):
        """テンプレートコピーテスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        # テンプレートコピー
        result = export_service.copy_templates_to_folder(folders["root"])

        assert result["dtd_copied"] == True
        assert result["xsl_copied"] == True
        assert os.path.exists(os.path.join(folders["root"], "PHOTO05.DTD"))
        assert os.path.exists(os.path.join(folders["root"], "PHOTO05.XSL"))

    def test_save_photo_xml(self, export_service, tmp_path):
        """PHOTO.XML保存テスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        xml_content = (
            '<?xml version="1.0" encoding="Shift_JIS"?><photodata></photodata>'
        )
        xml_path = export_service.save_photo_xml(folders["root"], xml_content)

        assert os.path.exists(xml_path)
        assert xml_path == os.path.join(folders["root"], "PHOTO.XML")

        # ファイル内容確認
        with open(xml_path, "r", encoding="shift_jis") as f:
            content = f.read()
            assert "photodata" in content

    def test_create_zip_archive(self, export_service, tmp_path):
        """ZIPアーカイブ作成テスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        # ダミーファイル作成
        pic_file = Path(folders["pic"]) / "P0000001.JPG"
        pic_file.write_text("dummy image")

        # ZIP作成
        zip_path = export_service.create_zip_archive(folders["root"], str(tmp_path))

        assert os.path.exists(zip_path)
        assert zip_path.endswith(".zip")

        # ZIP内容確認
        with zipfile.ZipFile(zip_path, "r") as zf:
            file_list = zf.namelist()
            assert any("PIC/P0000001.JPG" in f for f in file_list)

    def test_get_zip_file_size(self, export_service, tmp_path):
        """ZIPファイルサイズ取得テスト"""
        export_dir = tmp_path / "export_test"
        folders = export_service.create_folder_structure(str(export_dir))

        # ダミーファイル作成
        pic_file = Path(folders["pic"]) / "P0000001.JPG"
        pic_file.write_text("dummy image")

        # ZIP作成
        zip_path = export_service.create_zip_archive(folders["root"], str(tmp_path))

        # サイズ取得
        file_size = export_service.get_file_size(zip_path)
        assert file_size > 0

    def test_export_package(self, export_service, photo_data_list, tmp_path):
        """エクスポートパッケージ作成テスト（統合）"""
        # エクスポート実行
        result = export_service.export_package(
            photos=photo_data_list,
            xml_content='<?xml version="1.0"?><photodata></photodata>',
            export_dir=str(tmp_path),
            project_name="test_project",
        )

        assert result["success"] == True
        assert result["zip_path"] is not None
        assert result["total_photos"] == 3
        assert os.path.exists(result["zip_path"])

    def test_export_package_validation_errors(self, export_service, tmp_path):
        """エクスポート時バリデーションエラーテスト"""
        # 空の写真リスト
        result = export_service.export_package(
            photos=[],
            xml_content='<?xml version="1.0"?><photodata></photodata>',
            export_dir=str(tmp_path),
            project_name="test_project",
        )

        assert result["success"] == False
        assert len(result["errors"]) > 0

    def test_cleanup_temp_files(self, export_service, tmp_path):
        """一時ファイルクリーンアップテスト"""
        # ダミーファイル作成
        temp_file = tmp_path / "temp_file.txt"
        temp_file.write_text("temporary")

        # クリーンアップ
        export_service.cleanup_temp_files(str(tmp_path))

        # ファイルが削除されているか確認
        assert not os.path.exists(temp_file)
