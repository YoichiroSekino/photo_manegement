"""
PHOTO.XML生成 レスポンススキーマ
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PhotoXMLGenerationRequest(BaseModel):
    """PHOTO.XML生成リクエスト"""

    photo_ids: List[int] = Field(..., description="写真IDリスト")
    project_name: Optional[str] = Field(None, description="工事名称")
    contractor: Optional[str] = Field(None, description="施工業者名")


class PhotoXMLGenerationResponse(BaseModel):
    """PHOTO.XML生成レスポンス"""

    total_photos: int = Field(..., description="写真総数")
    xml_content: str = Field(..., description="生成されたXML内容")
    file_size: int = Field(..., description="XMLファイルサイズ（バイト）")
    validation_errors: List[str] = Field(
        default_factory=list, description="バリデーションエラー"
    )
    status: str = Field(..., description="処理ステータス")


class PhotoXMLValidationResponse(BaseModel):
    """PHOTO.XMLバリデーションレスポンス"""

    is_valid: bool = Field(..., description="バリデーション結果")
    errors: List[str] = Field(default_factory=list, description="エラーリスト")
    warnings: List[str] = Field(default_factory=list, description="警告リスト")
