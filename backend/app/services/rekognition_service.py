"""
Amazon Rekognition 画像分類サービス
"""

from typing import List, Dict, Optional
import boto3
from pydantic import BaseModel


class ImageLabel(BaseModel):
    """画像ラベル"""

    name: str
    confidence: float
    parents: List[str] = []


class RekognitionService:
    """Amazon Rekognition画像分類サービス"""

    # 建設関連キーワード
    CONSTRUCTION_KEYWORDS = {
        "equipment": [
            "excavator",
            "bulldozer",
            "crane",
            "dump truck",
            "loader",
            "backhoe",
            "forklift",
            "roller",
            "grader",
            "machinery",
            "vehicle",
            "truck",
        ],
        "people": ["worker", "person", "people", "engineer", "contractor"],
        "safety": [
            "helmet",
            "hard hat",
            "safety vest",
            "safety equipment",
            "protective gear",
        ],
        "materials": [
            "concrete",
            "rebar",
            "steel",
            "wood",
            "brick",
            "pipe",
            "scaffolding",
            "lumber",
        ],
        "scene": [
            "construction",
            "construction site",
            "building",
            "infrastructure",
            "road",
            "bridge",
        ],
    }

    def __init__(self, confidence_threshold: float = 70.0):
        """
        初期化

        Args:
            confidence_threshold: 信頼度閾値（この値以上のラベルのみ抽出）
        """
        self.confidence_threshold = confidence_threshold
        self.rekognition = boto3.client("rekognition")

    def detect_labels_from_image(
        self, s3_bucket: str, s3_key: str, max_labels: int = 50
    ) -> List[Dict]:
        """
        S3画像からラベルを検出

        Args:
            s3_bucket: S3バケット名
            s3_key: S3オブジェクトキー
            max_labels: 最大ラベル数

        Returns:
            検出されたラベルのリスト
        """
        response = self.rekognition.detect_labels(
            Image={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}},
            MaxLabels=max_labels,
            MinConfidence=self.confidence_threshold,
        )

        labels = []
        for label in response.get("Labels", []):
            if label["Confidence"] >= self.confidence_threshold:
                labels.append(
                    {
                        "Name": label["Name"],
                        "Confidence": label["Confidence"],
                        "Parents": [p["Name"] for p in label.get("Parents", [])],
                    }
                )

        return labels

    def categorize_construction_labels(
        self, labels: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        建設関連ラベルをカテゴリ分類

        Args:
            labels: ラベルリスト

        Returns:
            カテゴリ別ラベル辞書
        """
        categorized = {
            "equipment": [],
            "people": [],
            "safety": [],
            "materials": [],
            "scene": [],
            "other": [],
        }

        for label in labels:
            label_name = label["Name"].lower()
            categorized_flag = False

            for category, keywords in self.CONSTRUCTION_KEYWORDS.items():
                if any(keyword in label_name for keyword in keywords):
                    categorized[category].append(label["Name"])
                    categorized_flag = True
                    break

            if not categorized_flag:
                categorized["other"].append(label["Name"])

        return categorized

    def filter_construction_related(self, labels: List[Dict]) -> List[Dict]:
        """
        建設関連ラベルのみをフィルタリング

        Args:
            labels: 全ラベルリスト

        Returns:
            建設関連ラベルのみのリスト
        """
        all_keywords = [
            keyword
            for keywords in self.CONSTRUCTION_KEYWORDS.values()
            for keyword in keywords
        ]

        filtered = []
        for label in labels:
            label_name = label["Name"].lower()
            if any(keyword in label_name for keyword in all_keywords):
                filtered.append(label)

        return filtered

    def create_image_label_summary(self, labels: List[Dict]) -> Dict:
        """
        画像ラベルのサマリー作成

        Args:
            labels: ラベルリスト

        Returns:
            サマリー情報
        """
        if not labels:
            return {
                "total_labels": 0,
                "max_confidence": 0.0,
                "avg_confidence": 0.0,
                "top_labels": [],
                "has_construction_content": False,
            }

        confidences = [label["Confidence"] for label in labels]
        sorted_labels = sorted(labels, key=lambda x: x["Confidence"], reverse=True)

        # 建設関連コンテンツの有無
        construction_related = self.filter_construction_related(labels)

        return {
            "total_labels": len(labels),
            "max_confidence": max(confidences),
            "avg_confidence": sum(confidences) / len(confidences),
            "top_labels": [label["Name"] for label in sorted_labels[:5]],
            "has_construction_content": len(construction_related) > 0,
        }
