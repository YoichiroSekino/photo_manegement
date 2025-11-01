"""
OCRサービス - Amazon Textractを使用した黒板テキスト抽出
"""

import re
import boto3
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class BlackboardData(BaseModel):
    """黒板から抽出されたデータ"""

    work_name: Optional[str] = None  # 工事名
    work_type: Optional[str] = None  # 工種
    work_kind: Optional[str] = None  # 種別
    work_detail: Optional[str] = None  # 細別
    station: Optional[str] = None  # 測点
    shooting_date: Optional[str] = None  # 撮影日
    design_dimension: Optional[int] = None  # 設計寸法
    actual_dimension: Optional[int] = None  # 実測寸法
    inspector: Optional[str] = None  # 立会者
    remarks: Optional[str] = None  # 備考


class OCRService:
    """OCRサービス"""

    def __init__(self, confidence_threshold: float = 70.0, region: str = "ap-northeast-1"):
        """
        Args:
            confidence_threshold: テキスト認識の信頼度閾値（0-100）
            region: AWSリージョン
        """
        self.confidence_threshold = confidence_threshold
        self.textract = boto3.client("textract", region_name=region)

    def extract_text_from_image(
        self, s3_bucket: str, s3_key: str
    ) -> List[Dict[str, any]]:
        """
        S3上の画像からテキストを抽出

        Args:
            s3_bucket: S3バケット名
            s3_key: S3キー

        Returns:
            抽出されたテキストブロックのリスト
        """
        response = self.textract.detect_document_text(
            Document={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}}
        )

        extracted_text = []
        for block in response.get("Blocks", []):
            if block["BlockType"] == "LINE":
                extracted_text.append(
                    {"text": block["Text"], "confidence": block["Confidence"]}
                )

        return extracted_text

    def parse_blackboard_text(self, text_blocks: List[Dict]) -> BlackboardData:
        """
        黒板テキストから工事情報を抽出

        Args:
            text_blocks: テキストブロックのリスト

        Returns:
            BlackboardData: 抽出された工事情報
        """
        data = BlackboardData()

        for block in text_blocks:
            text = block["text"]
            confidence = block["confidence"]

            # 信頼度が閾値未満のものはスキップ
            if confidence < self.confidence_threshold:
                continue

            # 工事名の抽出
            if "工事" in text and not data.work_name:
                data.work_name = text.strip()

            # 工種の抽出
            elif "工種" in text or "工種：" in text or "工種:" in text:
                work_type = self._extract_after_colon(text, "工種")
                if work_type:
                    data.work_type = work_type

            # 種別の抽出
            elif "種別" in text or "種別：" in text or "種別:" in text:
                work_kind = self._extract_after_colon(text, "種別")
                if work_kind:
                    data.work_kind = work_kind

            # 測点の抽出
            elif "測点" in text or "No." in text or "No" in text:
                station = self.extract_station_number(text)
                if station:
                    data.station = station

            # 撮影日の抽出
            elif "撮影日" in text or "日付" in text:
                date = self.extract_date(text)
                if date:
                    data.shooting_date = date

            # 立会者の抽出
            elif "立会" in text or "立会者" in text:
                inspector = self._extract_after_colon(text, "立会者")
                if not inspector:
                    inspector = self._extract_after_colon(text, "立会")
                if inspector:
                    data.inspector = inspector

            # 寸法情報の抽出
            if "設計" in text or "実測" in text:
                dimensions = self.extract_dimensions(text)
                if "design" in dimensions:
                    data.design_dimension = dimensions["design"]
                if "actual" in dimensions:
                    data.actual_dimension = dimensions["actual"]

        return data

    def extract_station_number(self, text: str) -> Optional[str]:
        """
        測点番号を抽出

        Args:
            text: テキスト

        Returns:
            測点番号（例: "100+5.0", "200"）
        """
        # まずスペースを除去
        text_normalized = re.sub(r"\s+", "", text)

        # パターン1: No.100+5.0 形式
        match = re.search(r"No\.?(\d+[\+\-]?\d*\.?\d*)", text_normalized, re.IGNORECASE)
        if match:
            return match.group(1)

        # パターン2: 測点100+5.0 形式
        match = re.search(r"測点(\d+[\+\-]?\d*\.?\d*)", text_normalized)
        if match:
            return match.group(1)

        return None

    def extract_dimensions(self, text: str) -> Dict[str, int]:
        """
        寸法情報を抽出

        Args:
            text: テキスト

        Returns:
            寸法辞書 {"design": 設計寸法, "actual": 実測寸法}
        """
        dimensions = {}

        # 設計寸法の抽出（複数パターン対応）
        # パターン: "設計：500mm", "設計寸法: 1200 mm"
        design_match = re.search(r"設計(?:寸法)?\s*[：:]?\s*(\d+)\s*mm?", text)
        if design_match:
            dimensions["design"] = int(design_match.group(1))

        # 実測寸法の抽出
        # パターン: "実測：498mm", "実測: 350mm"
        actual_match = re.search(r"実測(?:寸法)?\s*[：:]?\s*(\d+)\s*mm?", text)
        if actual_match:
            dimensions["actual"] = int(actual_match.group(1))

        return dimensions

    def extract_date(self, text: str) -> Optional[str]:
        """
        撮影日を抽出してYYYY-MM-DD形式に変換

        Args:
            text: テキスト

        Returns:
            日付文字列（YYYY-MM-DD形式）
        """
        # パターン1: YYYY-MM-DD または YYYY/MM/DD
        match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"

        # パターン2: 和暦（令和6年3月15日）
        match = re.search(r"令和(\d+)年(\d{1,2})月(\d{1,2})日", text)
        if match:
            reiwa_year, month, day = match.groups()
            year = 2018 + int(reiwa_year)  # 令和元年 = 2019年
            return f"{year}-{int(month):02d}-{int(day):02d}"

        # パターン3: 和暦（平成31年以前は扱わない）

        return None

    def _extract_after_colon(self, text: str, keyword: str) -> Optional[str]:
        """
        キーワードの後のコロン以降のテキストを抽出

        Args:
            text: テキスト
            keyword: キーワード

        Returns:
            抽出されたテキスト
        """
        pattern = f"{keyword}\\s*[：:]\\s*(.+?)(?:\\s|$)"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None
