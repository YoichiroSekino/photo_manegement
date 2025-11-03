"""
プロジェクト関連のPydanticスキーマ
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """プロジェクトベーススキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="プロジェクト名")
    description: Optional[str] = Field(None, description="説明")
    client_name: Optional[str] = Field(None, max_length=255, description="クライアント名")
    start_date: Optional[datetime] = Field(None, description="開始日")
    end_date: Optional[datetime] = Field(None, description="終了日")


class ProjectCreate(ProjectBase):
    """プロジェクト作成スキーマ"""

    pass


class ProjectUpdate(BaseModel):
    """プロジェクト更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="プロジェクト名")
    description: Optional[str] = Field(None, description="説明")
    client_name: Optional[str] = Field(None, max_length=255, description="クライアント名")
    start_date: Optional[datetime] = Field(None, description="開始日")
    end_date: Optional[datetime] = Field(None, description="終了日")


class ProjectResponse(ProjectBase):
    """プロジェクトレスポンススキーマ"""

    id: int = Field(..., description="プロジェクトID")
    organization_id: int = Field(..., description="組織ID")
    photo_count: Optional[int] = Field(0, description="写真数")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True


class ProjectStatsResponse(BaseModel):
    """プロジェクト統計レスポンススキーマ"""

    project_id: int = Field(..., description="プロジェクトID")
    photo_count: int = Field(..., description="総写真数")
    today_uploads: int = Field(..., description="今日のアップロード数")
    this_week_uploads: int = Field(..., description="今週のアップロード数")
    category_distribution: dict = Field(..., description="カテゴリ別分布")
    quality_issues_count: int = Field(..., description="品質問題のある写真数")
