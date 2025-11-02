"""
品質判定サービス

画像の品質を自動評価するサービス。
シャープネス（Laplacian分散）、明るさ、コントラストを計算し、
総合品質スコアと推奨アクションを生成します。
"""

import boto3
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List


class QualityAssessmentService:
    """品質判定サービスクラス"""

    def __init__(self):
        """初期化"""
        self.s3_client = boto3.client("s3")

        # 品質判定の閾値
        self.thresholds = {
            "sharpness": {"excellent": 300, "good": 150, "fair": 50},
            "brightness": {
                "min": 50,
                "max": 220,
                "optimal_min": 80,
                "optimal_max": 180,
            },
            "contrast": {"excellent": 60, "good": 40, "fair": 20},
        }

    def calculate_sharpness(self, image_data: bytes) -> float:
        """
        シャープネス（鮮明度）を計算

        Laplacian分散を使用してブレの程度を判定します。
        値が高いほど鮮明な画像です。

        Args:
            image_data: 画像データ（バイナリ）

        Returns:
            float: シャープネス値（Laplacian分散）
        """
        # PILで画像を開く
        img = Image.open(BytesIO(image_data))

        # グレースケールに変換
        gray = img.convert("L")

        # NumPy配列に変換
        gray_array = np.array(gray)

        # Laplacianフィルタを適用
        laplacian = cv2.Laplacian(gray_array, cv2.CV_64F)

        # 分散を計算（シャープネス指標）
        variance = laplacian.var()

        return float(variance)

    def calculate_brightness(self, image_data: bytes) -> float:
        """
        明るさを計算

        画像全体の平均輝度を計算します。
        0（暗い）から255（明るい）の範囲です。

        Args:
            image_data: 画像データ（バイナリ）

        Returns:
            float: 明るさ値（0-255）
        """
        # PILで画像を開く
        img = Image.open(BytesIO(image_data))

        # グレースケールに変換
        gray = img.convert("L")

        # NumPy配列に変換
        gray_array = np.array(gray)

        # 平均輝度を計算
        brightness = float(np.mean(gray_array))

        return brightness

    def calculate_contrast(self, image_data: bytes) -> float:
        """
        コントラストを計算

        輝度値の標準偏差を計算してコントラストを評価します。
        値が高いほどコントラストが強い画像です。

        Args:
            image_data: 画像データ（バイナリ）

        Returns:
            float: コントラスト値（標準偏差）
        """
        # PILで画像を開く
        img = Image.open(BytesIO(image_data))

        # グレースケールに変換
        gray = img.convert("L")

        # NumPy配列に変換
        gray_array = np.array(gray)

        # 標準偏差を計算（コントラスト指標）
        contrast = float(np.std(gray_array))

        return contrast

    def _get_quality_grade(self, score: float) -> str:
        """
        品質スコアからグレードを判定

        Args:
            score: 品質スコア（0-100）

        Returns:
            str: 品質グレード（excellent/good/fair/poor）
        """
        if score >= 80:
            return "excellent"
        elif score >= 65:
            return "good"
        elif score >= 45:
            return "fair"
        else:
            return "poor"

    def _detect_issues(
        self, sharpness: float, brightness: float, contrast: float
    ) -> List[str]:
        """
        品質の問題点を検出

        Args:
            sharpness: シャープネス値
            brightness: 明るさ値
            contrast: コントラスト値

        Returns:
            List[str]: 検出された問題点のリスト
        """
        issues = []

        # シャープネスチェック
        if sharpness < self.thresholds["sharpness"]["fair"]:
            issues.append("画像がぼやけています（ブレまたはピントずれの可能性）")

        # 明るさチェック
        if brightness < self.thresholds["brightness"]["min"]:
            issues.append("画像が暗すぎます（露出不足）")
        elif brightness > self.thresholds["brightness"]["max"]:
            issues.append("画像が明るすぎます（露出オーバー）")
        elif brightness < self.thresholds["brightness"]["optimal_min"]:
            issues.append("画像がやや暗いです")
        elif brightness > self.thresholds["brightness"]["optimal_max"]:
            issues.append("画像がやや明るいです")

        # コントラストチェック
        if contrast < self.thresholds["contrast"]["fair"]:
            issues.append("コントラストが低いです（メリハリがない）")

        return issues

    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """
        問題点に基づいて推奨アクションを生成

        Args:
            issues: 検出された問題点のリスト

        Returns:
            List[str]: 推奨アクションのリスト
        """
        recommendations = []

        for issue in issues:
            if "ぼやけ" in issue or "ブレ" in issue:
                recommendations.append(
                    "再撮影してください（手ブレ防止、三脚使用を推奨）"
                )
            elif "暗すぎ" in issue:
                recommendations.append(
                    "明るい場所で撮影するか、フラッシュを使用してください"
                )
            elif "明るすぎ" in issue:
                recommendations.append("露出を下げるか、逆光を避けて撮影してください")
            elif "やや暗い" in issue:
                recommendations.append("照明を追加するか、露出補正を検討してください")
            elif "やや明るい" in issue:
                recommendations.append("露出を調整することを検討してください")
            elif "コントラスト" in issue:
                recommendations.append("コントラストの高い背景で撮影してください")

        if not recommendations:
            recommendations.append("品質は良好です。そのまま使用できます。")

        return recommendations

    def assess_quality(self, image_data: bytes) -> Dict:
        """
        画像の総合品質評価

        Args:
            image_data: 画像データ（バイナリ）

        Returns:
            Dict: 品質評価結果
                - sharpness: シャープネス値
                - brightness: 明るさ値
                - contrast: コントラスト値
                - quality_score: 総合品質スコア（0-100）
                - quality_grade: 品質グレード
                - issues: 検出された問題点
                - recommendations: 推奨アクション
        """
        # 各指標を計算
        sharpness = self.calculate_sharpness(image_data)
        brightness = self.calculate_brightness(image_data)
        contrast = self.calculate_contrast(image_data)

        # シャープネススコア（0-40点）
        if sharpness >= self.thresholds["sharpness"]["excellent"]:
            sharpness_score = 40
        elif sharpness >= self.thresholds["sharpness"]["good"]:
            sharpness_score = 30
        elif sharpness >= self.thresholds["sharpness"]["fair"]:
            sharpness_score = 20
        else:
            sharpness_score = 10

        # 明るさスコア（0-30点）
        optimal_min = self.thresholds["brightness"]["optimal_min"]
        optimal_max = self.thresholds["brightness"]["optimal_max"]
        if optimal_min <= brightness <= optimal_max:
            brightness_score = 30
        elif (
            self.thresholds["brightness"]["min"]
            <= brightness
            <= self.thresholds["brightness"]["max"]
        ):
            brightness_score = 20
        else:
            brightness_score = 10

        # コントラストスコア（0-30点）
        if contrast >= self.thresholds["contrast"]["excellent"]:
            contrast_score = 30
        elif contrast >= self.thresholds["contrast"]["good"]:
            contrast_score = 20
        elif contrast >= self.thresholds["contrast"]["fair"]:
            contrast_score = 15
        else:
            contrast_score = 5

        # 総合スコア（0-100点）
        quality_score = sharpness_score + brightness_score + contrast_score

        # 品質グレード判定
        quality_grade = self._get_quality_grade(quality_score)

        # 問題点検出
        issues = self._detect_issues(sharpness, brightness, contrast)

        # 推奨アクション生成
        recommendations = self._generate_recommendations(issues)

        return {
            "sharpness": sharpness,
            "brightness": brightness,
            "contrast": contrast,
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "issues": issues,
            "recommendations": recommendations,
        }

    def download_image_from_s3(self, bucket: str, key: str) -> bytes:
        """
        S3から画像をダウンロード

        Args:
            bucket: S3バケット名
            key: S3オブジェクトキー

        Returns:
            bytes: 画像データ
        """
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response["Body"].read()
        return image_data
