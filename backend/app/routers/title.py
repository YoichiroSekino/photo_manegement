"""
タイトル自動生成 API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.title import (
    TitleGenerationResponse,
    TitleUpdateRequest,
)
from app.services.title_generation_service import TitleGenerationService

router = APIRouter(prefix="/api/v1/photos", tags=["Title Generation"])


@router.post("/{photo_id}/generate-title", response_model=TitleGenerationResponse)
async def generate_title(photo_id: int, db: Session = Depends(get_db)):
    """
    写真のタイトルを自動生成

    OCRデータと画像分類結果を使用してタイトルを生成します。

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        TitleGenerationResponse: タイトル生成結果

    Raises:
        HTTPException: 写真が見つからない場合
    """
    # 写真取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    try:
        # OCRデータ取得
        ocr_data = {}
        if photo.photo_metadata and "ocr_result" in photo.photo_metadata:
            ocr_result = photo.photo_metadata["ocr_result"]
            ocr_data = {
                "work_type": ocr_result.get("work_type"),
                "work_kind": ocr_result.get("work_kind"),
                "station": ocr_result.get("station"),
                "shooting_date": ocr_result.get("shooting_date"),
            }

        # 分類データ取得
        classification_data = {}
        if photo.photo_metadata and "rekognition_labels" in photo.photo_metadata:
            classification_data = photo.photo_metadata["rekognition_labels"]

        # タイトル生成
        service = TitleGenerationService()
        result = service.generate_title_with_metadata(
            ocr_data=ocr_data, classification_data=classification_data
        )

        # データベースに保存
        photo.title = result["title"]

        if photo.photo_metadata is None:
            photo.photo_metadata = {}

        photo.photo_metadata["generated_title"] = {
            "title": result["title"],
            "work_type": result["work_type"],
            "station": result["station"],
            "subject": result["subject"],
            "date": result["date"],
            "confidence": result["confidence"],
        }

        db.commit()
        db.refresh(photo)

        return TitleGenerationResponse(
            photo_id=photo_id,
            title=result["title"],
            work_type=result["work_type"],
            station=result["station"],
            subject=result["subject"],
            date=result["date"],
            confidence=result["confidence"],
            status="completed",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"タイトル生成に失敗しました: {str(e)}"
        )


@router.put("/{photo_id}/title", response_model=TitleGenerationResponse)
async def update_title(
    photo_id: int, request: TitleUpdateRequest, db: Session = Depends(get_db)
):
    """
    写真のタイトルを手動更新

    Args:
        photo_id: 写真ID
        request: タイトル更新リクエスト
        db: データベースセッション

    Returns:
        TitleGenerationResponse: 更新結果

    Raises:
        HTTPException: 写真が見つからない場合
    """
    # 写真取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    try:
        # タイトル更新
        photo.title = request.title

        if photo.photo_metadata is None:
            photo.photo_metadata = {}

        # 手動更新フラグを設定
        photo.photo_metadata["manual_title"] = True

        db.commit()
        db.refresh(photo)

        return TitleGenerationResponse(
            photo_id=photo_id,
            title=photo.title,
            work_type=None,
            station=None,
            subject=None,
            date=None,
            confidence=100.0,  # 手動更新は100%信頼度
            status="updated",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"タイトル更新に失敗しました: {str(e)}"
        )
