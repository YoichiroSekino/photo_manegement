"""
Amazon Rekognition レスポンススキーマ
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ImageLabelResponse(BaseModel):
    """画像ラベルレスポンス"""

    name: str = Field(..., description="ラベル名")
    confidence: float = Field(..., description="信頼度（0-100）", ge=0, le=100)
    parents: List[str] = Field(default_factory=list, description="親カテゴリ")


class ClassificationResponse(BaseModel):
    """画像分類レスポンス"""

    photo_id: int = Field(..., description="写真ID")
    status: str = Field(..., description="処理ステータス（completed/not_processed）")
    labels: List[ImageLabelResponse] = Field(
        default_factory=list, description="検出ラベル"
    )
    categorized_labels: Dict[str, List[str]] = Field(
        default_factory=dict, description="カテゴリ別ラベル"
    )
    summary: Dict = Field(default_factory=dict, description="サマリー情報")


class ClassificationResultResponse(BaseModel):
    """分類結果取得レスポンス"""

    photo_id: int = Field(..., description="写真ID")
    status: str = Field(..., description="処理ステータス")
    labels: List[ImageLabelResponse] = Field(
        default_factory=list, description="検出ラベル"
    )
    categorized_labels: Optional[Dict[str, List[str]]] = Field(
        None, description="カテゴリ別ラベル"
    )
    summary: Optional[Dict] = Field(None, description="サマリー情報")
