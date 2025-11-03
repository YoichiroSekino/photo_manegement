"""
写真関連のPydanticスキーマ
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class PhotoCategory(BaseModel):
    """写真カテゴリスキーマ"""

    major_category: Optional[str] = Field(None, description="写真-大分類")
    photo_type: Optional[str] = Field(None, description="写真区分")
    work_type: Optional[str] = Field(None, description="工種")
    work_kind: Optional[str] = Field(None, description="種別")
    work_detail: Optional[str] = Field(None, description="細別")


class PhotoBase(BaseModel):
    """写真ベーススキーマ"""

    file_name: str = Field(..., max_length=255, description="ファイル名")
    file_size: int = Field(..., gt=0, description="ファイルサイズ（バイト）")
    mime_type: str = Field(..., description="MIMEタイプ")
    s3_key: str = Field(..., max_length=500, description="S3キー")

    title: Optional[str] = Field(None, max_length=255, description="タイトル")
    description: Optional[str] = Field(None, description="説明")
    shooting_date: Optional[datetime] = Field(None, description="撮影日時")

    latitude: Optional[str] = Field(None, description="緯度")
    longitude: Optional[str] = Field(None, description="経度")
    location_address: Optional[str] = Field(None, description="住所")

    tags: Optional[List[str]] = Field(None, description="タグ")

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        """MIMEタイプのバリデーション"""
        allowed_types = ["image/jpeg", "image/tiff"]
        if v not in allowed_types:
            raise ValueError(
                f"無効なMIMEタイプです。許可されている形式: {', '.join(allowed_types)}"
            )
        return v


class PhotoCreate(PhotoBase):
    """写真作成スキーマ"""

    project_id: Optional[int] = Field(None, description="プロジェクトID")
    s3_url: Optional[str] = Field(None, max_length=500, description="S3 URL")
    major_category: Optional[str] = None
    photo_type: Optional[str] = None
    work_type: Optional[str] = None
    work_kind: Optional[str] = None
    work_detail: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PhotoUpdate(BaseModel):
    """写真更新スキーマ"""

    project_id: Optional[int] = Field(None, description="プロジェクトID")
    title: Optional[str] = None
    description: Optional[str] = None
    shooting_date: Optional[datetime] = None
    major_category: Optional[str] = None
    photo_type: Optional[str] = None
    work_type: Optional[str] = None
    tags: Optional[List[str]] = None


class PhotoResponse(PhotoBase):
    """写真レスポンススキーマ"""

    id: int
    organization_id: int
    project_id: Optional[int] = None
    s3_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    major_category: Optional[str] = None
    photo_type: Optional[str] = None
    work_type: Optional[str] = None
    work_kind: Optional[str] = None
    work_detail: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = Field(None, alias="photo_metadata")
    is_processed: bool = False
    is_representative: bool = False
    is_submission_frequency: bool = False

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        populate_by_name = True


class PhotoListResponse(BaseModel):
    """写真一覧レスポンススキーマ"""

    items: List[PhotoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
