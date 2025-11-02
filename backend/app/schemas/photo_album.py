"""
工事写真帳生成 スキーマ
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class LayoutType(str, Enum):
    """レイアウトタイプ"""

    STANDARD = "standard"  # 1ページ2枚
    COMPACT = "compact"  # 1ページ4枚
    DETAILED = "detailed"  # 1ページ1枚


class CoverData(BaseModel):
    """表紙データ"""

    project_name: Optional[str] = Field(None, description="工事名")
    contractor: Optional[str] = Field(None, description="施工業者名")
    period_from: Optional[str] = Field(None, description="工期開始日")
    period_to: Optional[str] = Field(None, description="工期終了日")
    location: Optional[str] = Field(None, description="施工場所")


class PhotoAlbumGenerationRequest(BaseModel):
    """写真帳生成リクエスト"""

    photo_ids: List[int] = Field(..., description="写真IDリスト")
    layout_type: LayoutType = Field(LayoutType.STANDARD, description="レイアウトタイプ")
    cover_data: Optional[CoverData] = Field(None, description="表紙データ")
    add_page_numbers: bool = Field(True, description="ページ番号を追加するか")
    header_text: Optional[str] = Field(None, description="ヘッダーテキスト")
    footer_text: Optional[str] = Field(None, description="フッターテキスト")


class PhotoAlbumGenerationResponse(BaseModel):
    """写真帳生成レスポンス"""

    success: bool = Field(..., description="成功フラグ")
    pdf_path: Optional[str] = Field(None, description="PDFファイルパス")
    download_url: Optional[str] = Field(None, description="ダウンロードURL")
    total_pages: int = Field(..., description="総ページ数")
    total_photos: int = Field(..., description="写真総数")
    file_size: Optional[int] = Field(None, description="ファイルサイズ（バイト）")
    errors: List[str] = Field(default_factory=list, description="エラーリスト")
    status: str = Field(..., description="処理ステータス")
