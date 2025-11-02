"""
工事写真帳生成サービス

PDF形式の工事写真帳を自動生成します
"""

import os
from enum import Enum
from typing import List, Dict, Optional
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PIL import Image


class LayoutType(Enum):
    """レイアウトタイプ"""

    STANDARD = "standard"  # 1ページ2枚
    COMPACT = "compact"  # 1ページ4枚
    DETAILED = "detailed"  # 1ページ1枚


class PhotoAlbumGenerator:
    """工事写真帳ジェネレータークラス"""

    def __init__(self):
        """初期化"""
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.title_font_size = 14
        self.body_font_size = 10

        # 日本語フォント登録
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
            self.font_name = "HeiseiMin-W3"
        except:
            # フォント登録失敗時はHelveticaを使用
            self.font_name = "Helvetica"

    def generate_pdf(
        self,
        photos: List[Dict],
        output_path: str,
        layout_type: LayoutType = LayoutType.STANDARD,
        cover_data: Optional[Dict] = None,
        add_page_numbers: bool = False,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict:
        """
        PDF写真帳を生成

        Args:
            photos: 写真データリスト
            output_path: 出力ファイルパス
            layout_type: レイアウトタイプ
            cover_data: 表紙データ（オプション）
            add_page_numbers: ページ番号を追加するか
            header_text: ヘッダーテキスト
            footer_text: フッターテキスト

        Returns:
            生成結果
        """
        # バリデーション
        if not photos or len(photos) == 0:
            return {
                "success": False,
                "errors": ["写真が指定されていません"],
                "pdf_path": None,
                "total_pages": 0,
                "total_photos": 0,
            }

        try:
            # PDFキャンバス作成
            c = canvas.Canvas(output_path, pagesize=A4)

            page_count = 0

            # 表紙ページ生成
            if cover_data:
                self._draw_cover_page(c, cover_data)
                c.showPage()
                page_count += 1

            # 写真ページ生成
            photo_pages = self._generate_photo_pages(photos, layout_type)
            for page_photos in photo_pages:
                self._draw_photo_page(
                    c,
                    page_photos,
                    layout_type,
                    header_text=header_text,
                    footer_text=footer_text,
                )

                # ページ番号追加
                if add_page_numbers:
                    page_count += 1
                    self._draw_page_number(c, page_count)

                c.showPage()

            # PDF保存
            c.save()

            # ファイルサイズ取得
            file_size = os.path.getsize(output_path)

            # ページ数計算
            total_pages = (
                page_count + len(photo_pages) if not add_page_numbers else page_count
            )

            return {
                "success": True,
                "errors": [],
                "pdf_path": output_path,
                "total_pages": total_pages,
                "total_photos": len(photos),
                "file_size": file_size,
                "has_page_numbers": add_page_numbers,
            }

        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "pdf_path": None,
                "total_pages": 0,
                "total_photos": 0,
            }

    def generate_cover_page_data(self, cover_data: Dict) -> Dict:
        """
        表紙ページデータを生成

        Args:
            cover_data: 表紙データ

        Returns:
            表紙情報
        """
        period = ""
        if cover_data.get("period_from") and cover_data.get("period_to"):
            period = f"{cover_data['period_from']} ～ {cover_data['period_to']}"

        return {
            "project_name": cover_data.get("project_name", ""),
            "contractor": cover_data.get("contractor", ""),
            "period": period,
            "location": cover_data.get("location", ""),
        }

    def _draw_cover_page(self, c: canvas.Canvas, cover_data: Dict):
        """
        表紙ページを描画

        Args:
            c: キャンバス
            cover_data: 表紙データ
        """
        cover_info = self.generate_cover_page_data(cover_data)

        # タイトル
        c.setFont(self.font_name, 24)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 100 * mm, "工事写真帳"
        )

        # 工事名
        c.setFont(self.font_name, 16)
        y_position = self.page_height - 150 * mm
        c.drawCentredString(self.page_width / 2, y_position, cover_info["project_name"])

        # 施工業者
        y_position -= 30 * mm
        c.setFont(self.font_name, 12)
        c.drawCentredString(
            self.page_width / 2, y_position, f"施工: {cover_info['contractor']}"
        )

        # 工期
        if cover_info["period"]:
            y_position -= 20 * mm
            c.drawCentredString(
                self.page_width / 2, y_position, f"工期: {cover_info['period']}"
            )

        # 場所
        if cover_info["location"]:
            y_position -= 20 * mm
            c.drawCentredString(
                self.page_width / 2, y_position, f"場所: {cover_info['location']}"
            )

    def _generate_photo_pages(
        self, photos: List[Dict], layout_type: LayoutType
    ) -> List[List[Dict]]:
        """
        写真をページごとに分割

        Args:
            photos: 写真データリスト
            layout_type: レイアウトタイプ

        Returns:
            ページごとの写真リスト
        """
        photos_per_page = {
            LayoutType.STANDARD: 2,
            LayoutType.COMPACT: 4,
            LayoutType.DETAILED: 1,
        }

        per_page = photos_per_page[layout_type]
        pages = []

        for i in range(0, len(photos), per_page):
            pages.append(photos[i : i + per_page])

        return pages

    def _draw_photo_page(
        self,
        c: canvas.Canvas,
        photos: List[Dict],
        layout_type: LayoutType,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ):
        """
        写真ページを描画

        Args:
            c: キャンバス
            photos: ページ内の写真リスト
            layout_type: レイアウトタイプ
            header_text: ヘッダーテキスト
            footer_text: フッターテキスト
        """
        # ヘッダー描画
        if header_text:
            c.setFont(self.font_name, 10)
            c.drawString(self.margin, self.page_height - self.margin, header_text)

        # フッター描画
        if footer_text:
            c.setFont(self.font_name, 10)
            c.drawString(self.margin, self.margin / 2, footer_text)

        # レイアウトに応じて写真配置
        if layout_type == LayoutType.STANDARD:
            self._draw_standard_layout(c, photos)
        elif layout_type == LayoutType.COMPACT:
            self._draw_compact_layout(c, photos)
        elif layout_type == LayoutType.DETAILED:
            self._draw_detailed_layout(c, photos)

    def _draw_standard_layout(self, c: canvas.Canvas, photos: List[Dict]):
        """標準レイアウト（1ページ2枚）を描画"""
        photo_height = (self.page_height - 3 * self.margin) / 2
        photo_width = self.page_width - 2 * self.margin

        for idx, photo in enumerate(photos):
            y_position = (
                self.page_height
                - self.margin
                - (idx + 1) * photo_height
                - idx * self.margin / 2
            )
            self._draw_single_photo(
                c, photo, self.margin, y_position, photo_width, photo_height
            )

    def _draw_compact_layout(self, c: canvas.Canvas, photos: List[Dict]):
        """コンパクトレイアウト（1ページ4枚）を描画"""
        photo_height = (self.page_height - 3 * self.margin) / 2
        photo_width = (self.page_width - 3 * self.margin) / 2

        positions = [
            (self.margin, self.page_height - self.margin - photo_height),  # 左上
            (
                self.page_width / 2 + self.margin / 2,
                self.page_height - self.margin - photo_height,
            ),  # 右上
            (
                self.margin,
                self.page_height - 2 * self.margin - 2 * photo_height,
            ),  # 左下
            (
                self.page_width / 2 + self.margin / 2,
                self.page_height - 2 * self.margin - 2 * photo_height,
            ),  # 右下
        ]

        for idx, photo in enumerate(photos):
            if idx < len(positions):
                x, y = positions[idx]
                self._draw_single_photo(c, photo, x, y, photo_width, photo_height)

    def _draw_detailed_layout(self, c: canvas.Canvas, photos: List[Dict]):
        """詳細レイアウト（1ページ1枚）を描画"""
        photo_height = self.page_height - 4 * self.margin
        photo_width = self.page_width - 2 * self.margin

        if len(photos) > 0:
            photo = photos[0]
            self._draw_single_photo(
                c, photo, self.margin, self.margin * 2, photo_width, photo_height
            )

    def _draw_single_photo(
        self,
        c: canvas.Canvas,
        photo: Dict,
        x: float,
        y: float,
        width: float,
        height: float,
    ):
        """
        単一写真を描画

        Args:
            c: キャンバス
            photo: 写真データ
            x: X座標
            y: Y座標
            width: 幅
            height: 高さ
        """
        # 画像描画
        image_data = photo.get("image_data")
        if image_data:
            try:
                # 画像をリサイズして描画
                img = Image.open(BytesIO(image_data))
                img_width, img_height = img.size

                # アスペクト比を保持してリサイズ
                aspect = img_width / img_height
                target_aspect = width / (height * 0.7)  # 画像エリアは高さの70%

                if aspect > target_aspect:
                    new_width = width
                    new_height = width / aspect
                else:
                    new_height = height * 0.7
                    new_width = new_height * aspect

                # 中央配置
                img_x = x + (width - new_width) / 2
                img_y = y + height * 0.3

                # 画像を一時ファイルに保存して描画（ReportLabの制約）
                temp_img = BytesIO()
                img.save(temp_img, format="JPEG")
                temp_img.seek(0)

                c.drawImage(temp_img, img_x, img_y, new_width, new_height)

            except Exception as e:
                # 画像読み込みエラーの場合はスキップ
                pass

        # タイトル描画
        c.setFont(self.font_name, 10)
        c.drawString(x + 5, y + 20, photo.get("title", ""))

        # メタデータ描画
        c.setFont(self.font_name, 8)
        c.drawString(x + 5, y + 10, f"撮影日: {photo.get('shooting_date', '')}")
        c.drawString(x + 5, y, f"工種: {photo.get('work_type', '')}")

    def _draw_page_number(self, c: canvas.Canvas, page_number: int):
        """
        ページ番号を描画

        Args:
            c: キャンバス
            page_number: ページ番号
        """
        c.setFont(self.font_name, 10)
        c.drawCentredString(self.page_width / 2, self.margin / 2, f"- {page_number} -")

    def resize_image(self, image_data: bytes, max_width: int, max_height: int) -> bytes:
        """
        画像をリサイズ

        Args:
            image_data: 画像データ
            max_width: 最大幅
            max_height: 最大高さ

        Returns:
            リサイズ後の画像データ
        """
        img = Image.open(BytesIO(image_data))
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=85)
        return output.getvalue()

    def generate_thumbnail(self, image_data: bytes, size: tuple) -> bytes:
        """
        サムネイルを生成

        Args:
            image_data: 画像データ
            size: サイズ (width, height)

        Returns:
            サムネイル画像データ
        """
        img = Image.open(BytesIO(image_data))
        img.thumbnail(size, Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=75)
        return output.getvalue()

    def get_page_count(self, photo_count: int, layout_type: LayoutType) -> int:
        """
        ページ数を計算

        Args:
            photo_count: 写真数
            layout_type: レイアウトタイプ

        Returns:
            ページ数
        """
        photos_per_page = {
            LayoutType.STANDARD: 2,
            LayoutType.COMPACT: 4,
            LayoutType.DETAILED: 1,
        }

        per_page = photos_per_page[layout_type]
        return (photo_count + per_page - 1) // per_page  # 切り上げ除算
