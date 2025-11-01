"""
OCR処理APIルーター
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import Photo
from app.services.ocr_service import OCRService, BlackboardData

router = APIRouter(prefix="/api/v1/photos", tags=["ocr"])


class OCRProcessResponse(BaseModel):
    """OCR処理レスポンス"""

    photo_id: int
    status: str
    blackboard_data: Optional[dict] = None


class OCRResultResponse(BaseModel):
    """OCR結果レスポンス"""

    photo_id: int
    status: str
    work_name: Optional[str] = None
    work_type: Optional[str] = None
    work_kind: Optional[str] = None
    station: Optional[str] = None
    shooting_date: Optional[str] = None
    design_dimension: Optional[int] = None
    actual_dimension: Optional[int] = None
    inspector: Optional[str] = None


@router.post("/{photo_id}/process-ocr", response_model=OCRProcessResponse)
async def process_ocr(photo_id: int, db: Session = Depends(get_db)):
    """
    写真のOCR処理を実行

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        OCR処理結果

    Raises:
        HTTPException: 写真が見つからない場合
    """
    # 写真を取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"写真が見つかりません（ID: {photo_id}）",
        )

    # OCRサービスを使用してテキスト抽出
    ocr_service = OCRService()

    # S3キーからバケット名とキーを分離（実際の実装では環境変数から取得）
    s3_bucket = "construction-photos"  # TODO: 環境変数から取得
    s3_key = photo.s3_key

    try:
        # テキスト抽出
        text_blocks = ocr_service.extract_text_from_image(s3_bucket, s3_key)

        # 黒板データ解析
        blackboard_data = ocr_service.parse_blackboard_text(text_blocks)

        # データベースに保存
        photo.major_category = "工事"  # OCR処理済みは工事として設定
        photo.work_type = blackboard_data.work_type
        photo.work_kind = blackboard_data.work_kind
        photo.work_detail = blackboard_data.work_detail

        if blackboard_data.shooting_date:
            from datetime import datetime

            photo.shooting_date = datetime.fromisoformat(blackboard_data.shooting_date)

        # メタデータに保存
        if not photo.photo_metadata:
            photo.photo_metadata = {}

        photo.photo_metadata["ocr_result"] = blackboard_data.model_dump()
        photo.photo_metadata["ocr_text_blocks"] = text_blocks

        photo.is_processed = True

        db.commit()
        db.refresh(photo)

        return OCRProcessResponse(
            photo_id=photo_id,
            status="completed",
            blackboard_data=blackboard_data.model_dump(),
        )

    except Exception as e:
        # OCR処理失敗
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR処理に失敗しました: {str(e)}",
        )


@router.get("/{photo_id}/ocr-result", response_model=OCRResultResponse)
async def get_ocr_result(photo_id: int, db: Session = Depends(get_db)):
    """
    写真のOCR結果を取得

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        OCR結果

    Raises:
        HTTPException: 写真が見つからない場合
    """
    # 写真を取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"写真が見つかりません（ID: {photo_id}）",
        )

    # OCR処理されているかチェック
    if not photo.is_processed or not photo.photo_metadata:
        return OCRResultResponse(photo_id=photo_id, status="not_processed")

    # メタデータからOCR結果を取得
    ocr_result = photo.photo_metadata.get("ocr_result", {})

    return OCRResultResponse(
        photo_id=photo_id,
        status="completed",
        work_name=ocr_result.get("work_name"),
        work_type=ocr_result.get("work_type"),
        work_kind=ocr_result.get("work_kind"),
        station=ocr_result.get("station"),
        shooting_date=ocr_result.get("shooting_date"),
        design_dimension=ocr_result.get("design_dimension"),
        actual_dimension=ocr_result.get("actual_dimension"),
        inspector=ocr_result.get("inspector"),
    )
