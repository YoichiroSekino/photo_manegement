"""
重複写真検出サービスのテスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image
from app.services.duplicate_detection_service import (
    DuplicateDetectionService,
    ImageHash,
    DuplicateGroup,
)


class TestDuplicateDetectionService:
    """DuplicateDetectionService のテスト"""

    @pytest.fixture
    def duplicate_service(self):
        """DuplicateDetectionServiceインスタンス"""
        return DuplicateDetectionService(similarity_threshold=90.0)

    def test_initialization(self, duplicate_service):
        """初期化テスト"""
        assert duplicate_service.similarity_threshold == 90.0
        assert duplicate_service.hash_size == 8  # デフォルト8x8

    def test_calculate_phash_success(self, duplicate_service):
        """pHash計算成功テスト"""
        # テスト用画像作成（100x100ピクセル、白色）
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        phash = duplicate_service.calculate_phash(img_bytes.getvalue())

        # pHashは16進数文字列（64bit = 16文字）
        assert isinstance(phash, str)
        assert len(phash) == 16
        assert all(c in "0123456789abcdef" for c in phash)

    def test_calculate_phash_different_images(self, duplicate_service):
        """異なる画像は異なるpHashを持つテスト"""
        # 白い画像
        img1 = Image.new("RGB", (100, 100), color="white")
        img1_bytes = BytesIO()
        img1.save(img1_bytes, format="JPEG")

        # 黒い画像
        img2 = Image.new("RGB", (100, 100), color="black")
        img2_bytes = BytesIO()
        img2.save(img2_bytes, format="JPEG")

        phash1 = duplicate_service.calculate_phash(img1_bytes.getvalue())
        phash2 = duplicate_service.calculate_phash(img2_bytes.getvalue())

        # 異なる画像は異なるハッシュ
        assert phash1 != phash2

    def test_calculate_phash_same_image(self, duplicate_service):
        """同じ画像は同じpHashを持つテスト"""
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes1 = BytesIO()
        img_bytes2 = BytesIO()
        img.save(img_bytes1, format="JPEG")
        img.save(img_bytes2, format="JPEG")

        phash1 = duplicate_service.calculate_phash(img_bytes1.getvalue())
        phash2 = duplicate_service.calculate_phash(img_bytes2.getvalue())

        # 同じ画像は同じハッシュ
        assert phash1 == phash2

    def test_calculate_hamming_distance(self, duplicate_service):
        """ハミング距離計算テスト"""
        # 完全一致
        hash1 = "0000000000000000"
        hash2 = "0000000000000000"
        distance = duplicate_service.calculate_hamming_distance(hash1, hash2)
        assert distance == 0

        # 1ビット異なる
        hash3 = "0000000000000000"
        hash4 = "0000000000000001"
        distance = duplicate_service.calculate_hamming_distance(hash3, hash4)
        assert distance == 1

        # 全ビット異なる
        hash5 = "0000000000000000"
        hash6 = "ffffffffffffffff"
        distance = duplicate_service.calculate_hamming_distance(hash5, hash6)
        assert distance == 64

    def test_calculate_similarity(self, duplicate_service):
        """類似度計算テスト"""
        # 完全一致: 100%
        hash1 = "0000000000000000"
        hash2 = "0000000000000000"
        similarity = duplicate_service.calculate_similarity(hash1, hash2)
        assert similarity == 100.0

        # 1ビット異なる: 約98.4%
        hash3 = "0000000000000000"
        hash4 = "0000000000000001"
        similarity = duplicate_service.calculate_similarity(hash3, hash4)
        assert 98.0 <= similarity <= 99.0

        # 全ビット異なる: 0%
        hash5 = "0000000000000000"
        hash6 = "ffffffffffffffff"
        similarity = duplicate_service.calculate_similarity(hash5, hash6)
        assert similarity == 0.0

    def test_are_duplicates_true(self, duplicate_service):
        """重複判定テスト（重複あり）"""
        # 完全一致
        hash1 = "0000000000000000"
        hash2 = "0000000000000000"
        assert duplicate_service.are_duplicates(hash1, hash2) is True

        # 95%類似（閾値90%以上）
        hash3 = "0000000000000000"
        hash4 = "000000000000000f"  # 4ビット異なる
        assert duplicate_service.are_duplicates(hash3, hash4) is True

    def test_are_duplicates_false(self, duplicate_service):
        """重複判定テスト（重複なし）"""
        # 50%類似（閾値90%未満）
        hash1 = "00000000ffffffff"
        hash2 = "ffffffff00000000"
        assert duplicate_service.are_duplicates(hash1, hash2) is False

    def test_find_duplicates_in_photos(self, duplicate_service):
        """写真リストから重複検出テスト"""
        photos = [
            {"id": 1, "phash": "0000000000000000"},  # グループ1
            {"id": 2, "phash": "0000000000000001"},  # グループ1（類似）
            {"id": 3, "phash": "ffffffffffffffff"},  # グループ2
            {"id": 4, "phash": "fffffffffffffff0"},  # グループ2（類似）
            {"id": 5, "phash": "aaaaaaaaaaaaaaaa"},  # 単独
        ]

        duplicate_groups = duplicate_service.find_duplicates_in_photos(photos)

        # 2つのグループが見つかる
        assert len(duplicate_groups) == 2

        # グループ1: ID 1, 2
        group1 = next(
            (g for g in duplicate_groups if 1 in [p["id"] for p in g.photos]), None
        )
        assert group1 is not None
        assert len(group1.photos) == 2
        assert {p["id"] for p in group1.photos} == {1, 2}

        # グループ2: ID 3, 4
        group2 = next(
            (g for g in duplicate_groups if 3 in [p["id"] for p in g.photos]), None
        )
        assert group2 is not None
        assert len(group2.photos) == 2
        assert {p["id"] for p in group2.photos} == {3, 4}

    def test_find_duplicates_no_duplicates(self, duplicate_service):
        """重複なしの場合のテスト"""
        photos = [
            {"id": 1, "phash": "0000000000000000"},
            {"id": 2, "phash": "ffffffffffffffff"},
            {"id": 3, "phash": "aaaaaaaaaaaaaaaa"},
        ]

        duplicate_groups = duplicate_service.find_duplicates_in_photos(photos)

        # 重複グループなし
        assert len(duplicate_groups) == 0

    def test_create_duplicate_summary(self, duplicate_service):
        """重複サマリー作成テスト"""
        duplicate_groups = [
            DuplicateGroup(
                photos=[
                    {"id": 1, "phash": "0000000000000000"},
                    {"id": 2, "phash": "0000000000000001"},
                ],
                avg_similarity=98.5,
            ),
            DuplicateGroup(
                photos=[
                    {"id": 3, "phash": "ffffffffffffffff"},
                    {"id": 4, "phash": "fffffffffffffff0"},
                    {"id": 5, "phash": "fffffffffffffff1"},
                ],
                avg_similarity=96.2,
            ),
        ]

        summary = duplicate_service.create_duplicate_summary(duplicate_groups)

        assert summary["total_groups"] == 2
        assert summary["total_duplicate_photos"] == 5
        assert summary["avg_similarity"] == pytest.approx((98.5 + 96.2) / 2, rel=1e-2)
        assert summary["largest_group_size"] == 3

    @patch("app.services.duplicate_detection_service.boto3.client")
    def test_download_image_from_s3(self, mock_boto_client):
        """S3から画像ダウンロードテスト"""
        # モックS3クライアント
        mock_s3 = Mock()
        mock_s3.get_object.return_value = {
            "Body": Mock(read=Mock(return_value=b"fake_image_data"))
        }
        mock_boto_client.return_value = mock_s3

        # 新しいインスタンスを作成（モック適用後）
        service = DuplicateDetectionService()

        image_data = service.download_image_from_s3(
            bucket="test-bucket", key="test.jpg"
        )

        assert image_data == b"fake_image_data"
        mock_s3.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="test.jpg"
        )
