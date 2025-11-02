"""
エクスポート レスポンススキーマ
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """エクスポートリクエスト"""

    photo_ids: List[int] = Field(..., description="写真IDリスト")
    project_name: Optional[str] = Field(None, description="プロジェクト名")
    contractor: Optional[str] = Field(None, description="施工業者名")
    include_drawings: bool = Field(False, description="参考図を含めるか")


class FileRenameInfo(BaseModel):
    """ファイルリネーム情報"""

    photo_id: int = Field(..., description="写真ID")
    original_file_name: str = Field(..., description="元のファイル名")
    new_file_name: str = Field(..., description="新しいファイル名")
    serial_number: int = Field(..., description="シリアル番号")


class ExportResponse(BaseModel):
    """エクスポートレスポンス"""

    success: bool = Field(..., description="成功フラグ")
    zip_path: Optional[str] = Field(None, description="ZIPファイルパス")
    download_url: Optional[str] = Field(None, description="ダウンロードURL")
    total_photos: int = Field(..., description="写真総数")
    file_size: Optional[int] = Field(None, description="ファイルサイズ（バイト）")
    file_renames: List[FileRenameInfo] = Field(
        default_factory=list, description="ファイルリネーム情報"
    )
    errors: List[str] = Field(default_factory=list, description="エラーリスト")
    status: str = Field(..., description="処理ステータス")


class ExportValidationResponse(BaseModel):
    """エクスポート前バリデーションレスポンス"""

    is_valid: bool = Field(..., description="バリデーション結果")
    total_photos: int = Field(..., description="写真総数")
    errors: List[str] = Field(default_factory=list, description="エラーリスト")
    warnings: List[str] = Field(default_factory=list, description="警告リスト")
    estimated_file_size: Optional[int] = Field(
        None, description="推定ファイルサイズ（バイト）"
    )
