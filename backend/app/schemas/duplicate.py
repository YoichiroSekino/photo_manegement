"""
重複写真検出 レスポンススキーマ
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class PhotoHashInfo(BaseModel):
    """写真ハッシュ情報"""

    photo_id: int = Field(..., description="写真ID")
    phash: str = Field(..., description="pHash（16進数文字列）")
    file_name: Optional[str] = Field(None, description="ファイル名")


class DuplicatePhotoInfo(BaseModel):
    """重複グループ内の写真情報"""

    id: int = Field(..., description="写真ID")
    file_name: str = Field(..., description="ファイル名")
    phash: str = Field(..., description="pHash")
    similarity: Optional[float] = Field(None, description="類似度（%）")


class DuplicateGroupResponse(BaseModel):
    """重複グループレスポンス"""

    group_id: int = Field(..., description="グループID")
    photos: List[DuplicatePhotoInfo] = Field(..., description="グループ内の写真")
    avg_similarity: float = Field(..., description="平均類似度（%）")
    photo_count: int = Field(..., description="グループ内写真数")


class DuplicateDetectionResponse(BaseModel):
    """重複検出レスポンス"""

    total_photos: int = Field(..., description="検出対象写真総数")
    duplicate_groups: List[DuplicateGroupResponse] = Field(
        ..., description="重複グループリスト"
    )
    summary: Dict = Field(..., description="サマリー情報")


class CalculateHashResponse(BaseModel):
    """ハッシュ計算レスポンス"""

    photo_id: int = Field(..., description="写真ID")
    phash: str = Field(..., description="計算されたpHash")
    status: str = Field(..., description="処理ステータス")


class DuplicateActionRequest(BaseModel):
    """重複確定・却下リクエスト"""

    photo_id_to_keep: int = Field(..., description="保持する写真ID")
    photo_id_to_delete: int = Field(..., description="削除する写真ID")
    action: str = Field(..., description="アクション (confirm/reject)")


class DuplicateActionResponse(BaseModel):
    """重複確定・却下レスポンス"""

    status: str = Field(..., description="処理ステータス")
    photo_id_kept: Optional[int] = Field(None, description="保持された写真ID")
    photo_id_deleted: Optional[int] = Field(None, description="削除された写真ID")
    message: str = Field(..., description="メッセージ")
