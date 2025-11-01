"""
検索関連のPydanticスキーマ
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.photo import PhotoResponse


class SearchQuery(BaseModel):
    """検索クエリスキーマ"""

    keyword: Optional[str] = Field(None, description="キーワード検索")
    work_type: Optional[str] = Field(None, description="工種フィルタ")
    work_kind: Optional[str] = Field(None, description="種別フィルタ")
    major_category: Optional[str] = Field(None, description="写真大分類フィルタ")
    photo_type: Optional[str] = Field(None, description="写真区分フィルタ")
    date_from: Optional[str] = Field(None, description="撮影日開始（YYYY-MM-DD）")
    date_to: Optional[str] = Field(None, description="撮影日終了（YYYY-MM-DD）")
    page: int = Field(1, ge=1, description="ページ番号")
    page_size: int = Field(20, ge=1, le=100, description="ページサイズ")


class SearchResponse(BaseModel):
    """検索結果レスポンススキーマ"""

    items: List[PhotoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    query: Optional[SearchQuery] = None
