"""
タイトル自動生成 レスポンススキーマ
"""

from typing import Optional
from pydantic import BaseModel, Field


class TitleGenerationRequest(BaseModel):
    """タイトル生成リクエスト"""

    photo_id: int = Field(..., description="写真ID")
    use_ocr: bool = Field(True, description="OCRデータを使用するか")
    use_classification: bool = Field(True, description="分類データを使用するか")


class TitleGenerationResponse(BaseModel):
    """タイトル生成レスポンス"""

    photo_id: int = Field(..., description="写真ID")
    title: str = Field(..., description="生成されたタイトル")
    work_type: Optional[str] = Field(None, description="工種")
    station: Optional[str] = Field(None, description="測点")
    subject: Optional[str] = Field(None, description="撮影対象")
    date: Optional[str] = Field(None, description="撮影日（YYYYMMDD）")
    confidence: float = Field(..., description="タイトル信頼度（0-100）")
    status: str = Field(..., description="処理ステータス")


class TitleUpdateRequest(BaseModel):
    """タイトル手動更新リクエスト"""

    title: str = Field(..., description="新しいタイトル", max_length=127)
