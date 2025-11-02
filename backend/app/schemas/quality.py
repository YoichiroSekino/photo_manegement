"""
品質判定 レスポンススキーマ
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QualityMetrics(BaseModel):
    """品質メトリクス"""

    sharpness: float = Field(..., description="シャープネス（Laplacian分散）")
    brightness: float = Field(..., description="明るさ（0-255）")
    contrast: float = Field(..., description="コントラスト（標準偏差）")


class QualityAssessmentResponse(BaseModel):
    """品質評価レスポンス"""

    photo_id: int = Field(..., description="写真ID")
    sharpness: float = Field(..., description="シャープネス値")
    brightness: float = Field(..., description="明るさ値（0-255）")
    contrast: float = Field(..., description="コントラスト値")
    quality_score: float = Field(..., description="総合品質スコア（0-100）")
    quality_grade: str = Field(
        ..., description="品質グレード（excellent/good/fair/poor）"
    )
    issues: List[str] = Field(..., description="検出された問題点")
    recommendations: List[str] = Field(..., description="推奨アクション")
    status: str = Field(..., description="処理ステータス")


class QualityCheckResponse(BaseModel):
    """品質チェックレスポンス"""

    photo_id: int = Field(..., description="写真ID")
    quality_score: float = Field(..., description="品質スコア（0-100）")
    quality_grade: str = Field(..., description="品質グレード")
    status: str = Field(..., description="ステータス（completed/exists）")
