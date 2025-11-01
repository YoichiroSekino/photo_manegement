"""
重複写真検出サービス
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import boto3
from PIL import Image
from io import BytesIO
import imagehash


@dataclass
class ImageHash:
    """画像ハッシュ情報"""

    photo_id: int
    phash: str


@dataclass
class DuplicateGroup:
    """重複グループ"""

    photos: List[Dict]
    avg_similarity: float


class DuplicateDetectionService:
    """重複写真検出サービス"""

    def __init__(self, similarity_threshold: float = 90.0, hash_size: int = 8):
        """
        初期化

        Args:
            similarity_threshold: 類似度閾値（この値以上を重複とみなす）
            hash_size: pHashのサイズ（デフォルト8x8）
        """
        self.similarity_threshold = similarity_threshold
        self.hash_size = hash_size
        self.s3_client = boto3.client("s3")

    def calculate_phash(self, image_data: bytes) -> str:
        """
        画像のpHash（Perceptual Hash）を計算

        Args:
            image_data: 画像データ（バイト列）

        Returns:
            16進数文字列のpHash
        """
        img = Image.open(BytesIO(image_data))
        phash = imagehash.phash(img, hash_size=self.hash_size)
        return str(phash)

    def calculate_hamming_distance(self, hash1: str, hash2: str) -> int:
        """
        2つのハッシュ間のハミング距離を計算

        Args:
            hash1: 1つ目のハッシュ（16進数文字列）
            hash2: 2つ目のハッシュ（16進数文字列）

        Returns:
            ハミング距離（異なるビット数）
        """
        # 16進数を整数に変換
        int1 = int(hash1, 16)
        int2 = int(hash2, 16)

        # XORで異なるビットを抽出し、1のビット数を数える
        xor = int1 ^ int2
        distance = bin(xor).count("1")

        return distance

    def calculate_similarity(self, hash1: str, hash2: str) -> float:
        """
        2つのハッシュ間の類似度を計算

        Args:
            hash1: 1つ目のハッシュ
            hash2: 2つ目のハッシュ

        Returns:
            類似度（0-100%）
        """
        distance = self.calculate_hamming_distance(hash1, hash2)
        max_distance = self.hash_size * self.hash_size  # 8x8 = 64ビット

        # 類似度 = (1 - distance / max_distance) * 100
        similarity = (1 - distance / max_distance) * 100

        return similarity

    def are_duplicates(self, hash1: str, hash2: str) -> bool:
        """
        2つのハッシュが重複しているか判定

        Args:
            hash1: 1つ目のハッシュ
            hash2: 2つ目のハッシュ

        Returns:
            重複している場合True
        """
        similarity = self.calculate_similarity(hash1, hash2)
        return similarity >= self.similarity_threshold

    def find_duplicates_in_photos(self, photos: List[Dict]) -> List[DuplicateGroup]:
        """
        写真リストから重複グループを検出

        Args:
            photos: 写真リスト（各写真は{"id": int, "phash": str}を含む）

        Returns:
            重複グループのリスト
        """
        if len(photos) < 2:
            return []

        # 重複グループを保持
        groups = []
        processed = set()

        for i, photo1 in enumerate(photos):
            if photo1["id"] in processed:
                continue

            # 現在の写真と類似する写真を探す
            similar_photos = [photo1]
            similarities = []

            for j, photo2 in enumerate(photos):
                if i == j or photo2["id"] in processed:
                    continue

                similarity = self.calculate_similarity(
                    photo1["phash"], photo2["phash"]
                )

                if similarity >= self.similarity_threshold:
                    similar_photos.append(photo2)
                    similarities.append(similarity)
                    processed.add(photo2["id"])

            # グループが2枚以上の場合のみ追加
            if len(similar_photos) >= 2:
                processed.add(photo1["id"])
                avg_similarity = sum(similarities) / len(similarities) if similarities else 100.0

                groups.append(
                    DuplicateGroup(photos=similar_photos, avg_similarity=avg_similarity)
                )

        return groups

    def create_duplicate_summary(self, duplicate_groups: List[DuplicateGroup]) -> Dict:
        """
        重複検出サマリーを作成

        Args:
            duplicate_groups: 重複グループリスト

        Returns:
            サマリー情報
        """
        if not duplicate_groups:
            return {
                "total_groups": 0,
                "total_duplicate_photos": 0,
                "avg_similarity": 0.0,
                "largest_group_size": 0,
            }

        total_photos = sum(len(group.photos) for group in duplicate_groups)
        avg_similarity = (
            sum(group.avg_similarity for group in duplicate_groups)
            / len(duplicate_groups)
        )
        largest_group_size = max(len(group.photos) for group in duplicate_groups)

        return {
            "total_groups": len(duplicate_groups),
            "total_duplicate_photos": total_photos,
            "avg_similarity": avg_similarity,
            "largest_group_size": largest_group_size,
        }

    def download_image_from_s3(self, bucket: str, key: str) -> bytes:
        """
        S3から画像をダウンロード

        Args:
            bucket: S3バケット名
            key: S3オブジェクトキー

        Returns:
            画像データ（バイト列）
        """
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
