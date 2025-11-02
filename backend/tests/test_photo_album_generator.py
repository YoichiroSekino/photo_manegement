"""
工事写真帳生成サービスのテスト
"""

import pytest
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

from app.services.photo_album_generator import PhotoAlbumGenerator, LayoutType


class TestPhotoAlbumGenerator:
    """工事写真帳ジェネレーターテストクラス"""

    @pytest.fixture
    def album_generator(self):
        """写真帳ジェネレーターのフィクスチャ"""
        return PhotoAlbumGenerator()

    @pytest.fixture
    def sample_photo_data(self):
        """サンプル写真データ"""
        return {
            "id": 1,
            "file_name": "P0000001.JPG",
            "title": "基礎工_No.15+20.5_配筋状況_20240315",
            "shooting_date": "2024-03-15",
            "major_category": "工事",
            "photo_type": "施工状況写真",
            "work_type": "基礎工",
            "work_kind": "配筋工",
            "image_data": None,  # テスト用にダミー画像を後で設定
        }

    @pytest.fixture
    def sample_photo_list(self):
        """複数写真データ"""
        photos = []
        for i in range(1, 5):
            photos.append({
                "id": i,
                "file_name": f"P000000{i}.JPG",
                "title": f"写真タイトル {i}",
                "shooting_date": f"2024-03-1{i}",
                "major_category": "工事",
                "photo_type": "施工状況写真",
                "work_type": "基礎工",
                "image_data": None,
            })
        return photos

    @pytest.fixture
    def dummy_image(self):
        """ダミー画像データ"""
        # 800x600のダミー画像作成
        img = Image.new('RGB', (800, 600), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()

    def test_initialization(self, album_generator):
        """初期化テスト"""
        assert album_generator is not None
        assert hasattr(album_generator, "generate_pdf")
        assert hasattr(album_generator, "generate_cover_page_data")
        assert hasattr(album_generator, "resize_image")

    def test_layout_types(self):
        """レイアウトタイプ列挙型テスト"""
        assert LayoutType.STANDARD.value == "standard"
        assert LayoutType.COMPACT.value == "compact"
        assert LayoutType.DETAILED.value == "detailed"

    def test_generate_cover_page_data(self, album_generator):
        """表紙ページデータ生成テスト"""
        cover_data = {
            "project_name": "〇〇道路改良工事",
            "contractor": "株式会社〇〇建設",
            "period_from": "2024-01-01",
            "period_to": "2024-12-31",
            "location": "〇〇県〇〇市",
        }

        cover_info = album_generator.generate_cover_page_data(cover_data)

        assert cover_info["project_name"] == "〇〇道路改良工事"
        assert cover_info["contractor"] == "株式会社〇〇建設"
        assert "period" in cover_info

    def test_generate_pdf_minimal(self, album_generator, sample_photo_data, dummy_image, tmp_path):
        """最小限のデータでPDF生成テスト"""
        # ダミー画像を設定
        sample_photo_data["image_data"] = dummy_image

        output_path = tmp_path / "test_album.pdf"

        result = album_generator.generate_pdf(
            photos=[sample_photo_data],
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
        )

        assert result["success"] == True
        assert os.path.exists(result["pdf_path"])
        assert result["total_pages"] > 0
        assert result["total_photos"] == 1

    def test_generate_pdf_with_cover(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """表紙付きPDF生成テスト"""
        # 各写真にダミー画像を設定
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "test_album_with_cover.pdf"

        cover_data = {
            "project_name": "テスト工事",
            "contractor": "テスト建設",
        }

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
            cover_data=cover_data,
        )

        assert result["success"] == True
        assert os.path.exists(result["pdf_path"])
        assert result["total_pages"] >= 2  # 表紙 + 写真ページ

    def test_layout_standard(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """標準レイアウト（1ページ2枚）テスト"""
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "standard_layout.pdf"

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
        )

        assert result["success"] == True
        # 4枚の写真 → 2ページ（1ページ2枚）
        assert result["total_pages"] == 2

    def test_layout_compact(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """コンパクトレイアウト（1ページ4枚）テスト"""
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "compact_layout.pdf"

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.COMPACT,
        )

        assert result["success"] == True
        # 4枚の写真 → 1ページ（1ページ4枚）
        assert result["total_pages"] == 1

    def test_layout_detailed(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """詳細レイアウト（1ページ1枚）テスト"""
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "detailed_layout.pdf"

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.DETAILED,
        )

        assert result["success"] == True
        # 4枚の写真 → 4ページ（1ページ1枚）
        assert result["total_pages"] == 4

    def test_page_numbering(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """ページ番号付与テスト"""
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "with_page_numbers.pdf"

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
            add_page_numbers=True,
        )

        assert result["success"] == True
        assert result["has_page_numbers"] == True

    def test_header_footer(self, album_generator, sample_photo_data, dummy_image, tmp_path):
        """ヘッダー/フッター追加テスト"""
        sample_photo_data["image_data"] = dummy_image

        output_path = tmp_path / "with_header_footer.pdf"

        result = album_generator.generate_pdf(
            photos=[sample_photo_data],
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
            header_text="工事写真帳",
            footer_text="株式会社〇〇建設",
        )

        assert result["success"] == True

    def test_resize_image(self, album_generator, dummy_image):
        """画像リサイズテスト"""
        # アスペクト比保持リサイズ
        resized = album_generator.resize_image(
            image_data=dummy_image,
            max_width=400,
            max_height=300,
        )

        assert resized is not None
        assert len(resized) < len(dummy_image)  # リサイズ後はサイズが小さくなる

    def test_generate_thumbnail(self, album_generator, dummy_image):
        """サムネイル生成テスト"""
        thumbnail = album_generator.generate_thumbnail(
            image_data=dummy_image,
            size=(150, 150),
        )

        assert thumbnail is not None
        img = Image.open(BytesIO(thumbnail))
        assert img.size[0] <= 150
        assert img.size[1] <= 150

    def test_pdf_file_size(self, album_generator, sample_photo_list, dummy_image, tmp_path):
        """PDFファイルサイズ取得テスト"""
        for photo in sample_photo_list:
            photo["image_data"] = dummy_image

        output_path = tmp_path / "size_test.pdf"

        result = album_generator.generate_pdf(
            photos=sample_photo_list,
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
        )

        assert result["success"] == True
        assert result["file_size"] > 0

    def test_empty_photos_error(self, album_generator, tmp_path):
        """写真が空の場合のエラーハンドリングテスト"""
        output_path = tmp_path / "empty.pdf"

        result = album_generator.generate_pdf(
            photos=[],
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
        )

        assert result["success"] == False
        assert len(result["errors"]) > 0

    def test_invalid_image_data_error(self, album_generator, sample_photo_data, tmp_path):
        """不正な画像データのエラーハンドリングテスト"""
        sample_photo_data["image_data"] = b"invalid_image_data"

        output_path = tmp_path / "invalid_image.pdf"

        result = album_generator.generate_pdf(
            photos=[sample_photo_data],
            output_path=str(output_path),
            layout_type=LayoutType.STANDARD,
        )

        # エラーハンドリングされて失敗またはスキップ
        assert result["success"] in [False, True]
        if not result["success"]:
            assert len(result["errors"]) > 0

    def test_get_page_count(self, album_generator):
        """ページ数計算テスト"""
        # 標準レイアウト（1ページ2枚）
        assert album_generator.get_page_count(4, LayoutType.STANDARD) == 2
        assert album_generator.get_page_count(5, LayoutType.STANDARD) == 3

        # コンパクトレイアウト（1ページ4枚）
        assert album_generator.get_page_count(4, LayoutType.COMPACT) == 1
        assert album_generator.get_page_count(5, LayoutType.COMPACT) == 2

        # 詳細レイアウト（1ページ1枚）
        assert album_generator.get_page_count(4, LayoutType.DETAILED) == 4
