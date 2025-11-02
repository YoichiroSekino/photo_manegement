"""
タイトル自動生成サービス

OCRデータと画像分類結果から写真タイトルを自動生成するサービス。
形式: [工種]_[測点]_[撮影対象]_[撮影日]
例: "基礎工_No.15+20.5_配筋状況_20240315"
"""

import re
from datetime import datetime
from typing import Dict, Optional


class TitleGenerationService:
    """タイトル自動生成サービスクラス"""

    def __init__(self):
        """初期化"""
        # 分類ラベルから撮影対象へのマッピング
        self.label_to_subject = {
            "excavator": "掘削重機",
            "crane": "クレーン",
            "dump truck": "ダンプトラック",
            "bulldozer": "ブルドーザー",
            "worker": "作業状況",
            "person": "作業員",
            "helmet": "安全装備",
            "safety vest": "安全装備",
            "concrete": "コンクリート",
            "rebar": "鉄筋",
            "steel": "鋼材",
            "construction": "施工状況",
        }

        # 工種から撮影対象へのマッピング
        self.work_type_to_subject = {
            "基礎工": "基礎施工",
            "土工": "土工作業",
            "配筋工": "配筋状況",
            "型枠工": "型枠設置",
            "コンクリート工": "コンクリート打設",
            "鉄筋工": "鉄筋組立",
            "舗装工": "舗装施工",
        }

    def generate_title(
        self, ocr_data: Dict, classification_data: Dict
    ) -> str:
        """
        写真タイトルを自動生成

        Args:
            ocr_data: OCRデータ（work_type, station, shooting_date等）
            classification_data: 分類データ（categorized_labels等）

        Returns:
            str: 生成されたタイトル
        """
        # 各要素を抽出
        work_type = ocr_data.get("work_type", "")
        station = self.format_station(ocr_data.get("station", ""))
        date = self.format_date(ocr_data.get("shooting_date", ""))

        # 撮影対象を推定
        subject = ""
        if work_type:
            subject = self.infer_subject_from_work_type(work_type)
        elif classification_data:
            subject = self.infer_subject_from_classification(classification_data)

        # タイトル構築
        title_parts = []

        if work_type:
            title_parts.append(work_type)

        if station:
            title_parts.append(station)

        if subject:
            title_parts.append(subject)
        elif not work_type:
            # 工種も撮影対象もない場合
            title_parts.append("工事写真")

        if date:
            title_parts.append(date)

        title = "_".join(title_parts)

        # バリデーションと整形
        title = self.validate_title(title)

        # デフォルトタイトル
        if not title or title == "":
            title = f"工事写真_{date if date else self.format_date('')}"

        return title

    def format_station(self, station: Optional[str]) -> str:
        """
        測点を標準形式にフォーマット

        Args:
            station: 測点文字列

        Returns:
            str: フォーマットされた測点（例: "No.15+20.5"）
        """
        if not station:
            return ""

        # "No."を除去して数値部分を抽出
        station_cleaned = re.sub(r"測点|No\.|no\.", "", station).strip()

        # 空の場合は空文字を返す
        if not station_cleaned:
            return ""

        # "No."を付加
        if not station_cleaned.startswith("No."):
            station_cleaned = f"No.{station_cleaned}"

        return station_cleaned

    def format_date(self, date_str: Optional[str]) -> str:
        """
        日付をYYYYMMDD形式にフォーマット

        Args:
            date_str: 日付文字列

        Returns:
            str: YYYYMMDD形式の日付
        """
        if not date_str:
            # 日付がない場合は今日の日付
            return datetime.now().strftime("%Y%m%d")

        # 様々な日付形式に対応
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%Y%m%d",
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y%m%d")
            except ValueError:
                continue

        # パースできない場合は今日の日付
        return datetime.now().strftime("%Y%m%d")

    def infer_subject_from_classification(
        self, classification_data: Dict
    ) -> str:
        """
        分類データから撮影対象を推定

        Args:
            classification_data: 分類データ

        Returns:
            str: 推定された撮影対象
        """
        if not classification_data or "categorized_labels" not in classification_data:
            return ""

        categorized = classification_data["categorized_labels"]

        # 優先順位: equipment > people > safety > materials > scene
        priority_categories = [
            "equipment",
            "people",
            "safety",
            "materials",
            "scene",
        ]

        for category in priority_categories:
            if category in categorized and categorized[category]:
                # 最初のラベルを使用
                label = categorized[category][0]
                subject = self.label_to_subject.get(label, label)
                return subject

        return "施工状況"

    def infer_subject_from_work_type(self, work_type: str) -> str:
        """
        工種から撮影対象を推定

        Args:
            work_type: 工種

        Returns:
            str: 推定された撮影対象
        """
        return self.work_type_to_subject.get(work_type, f"{work_type}状況")

    def validate_title(self, title: str) -> str:
        """
        タイトルをバリデーション

        デジタル写真管理情報基準に準拠:
        - 最大127文字（全角・半角混在可）
        - 無効な文字（<, >, :, ", /, \\, |, ?, *）を除去

        Args:
            title: タイトル

        Returns:
            str: バリデーション済みタイトル
        """
        if not title:
            return ""

        # 無効な文字を除去
        invalid_chars = r'[<>:"/\\|?*]'
        title = re.sub(invalid_chars, "", title)

        # 最大127文字に制限
        if len(title) > 127:
            title = title[:127]

        return title.strip()

    def generate_title_with_metadata(
        self, ocr_data: Dict, classification_data: Dict
    ) -> Dict:
        """
        タイトルをメタデータ付きで生成

        Args:
            ocr_data: OCRデータ
            classification_data: 分類データ

        Returns:
            Dict: タイトルとメタデータ
        """
        work_type = ocr_data.get("work_type", "")
        station = self.format_station(ocr_data.get("station", ""))
        date = self.format_date(ocr_data.get("shooting_date", ""))

        # 撮影対象を推定
        subject = ""
        if work_type:
            subject = self.infer_subject_from_work_type(work_type)
        elif classification_data:
            subject = self.infer_subject_from_classification(classification_data)

        # タイトル生成
        title = self.generate_title(ocr_data, classification_data)

        # 信頼度計算（データの充実度）
        confidence = 0.0
        confidence_factors = 0

        if work_type:
            confidence += 30.0
            confidence_factors += 1

        if station:
            confidence += 20.0
            confidence_factors += 1

        if subject:
            confidence += 30.0
            confidence_factors += 1

        if date and ocr_data.get("shooting_date"):
            # OCRから取得した日付の場合は高信頼度
            confidence += 20.0
            confidence_factors += 1

        # 信頼度を0-100の範囲に正規化
        if confidence_factors > 0:
            confidence = confidence  # すでに100点満点で計算済み
        else:
            confidence = 10.0  # デフォルトタイトルの場合

        return {
            "title": title,
            "work_type": work_type if work_type else None,
            "station": station if station else None,
            "subject": subject if subject else None,
            "date": date if date else None,
            "confidence": round(confidence, 2),
        }
