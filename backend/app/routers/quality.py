"""
品質判定 API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.quality import (
    QualityAssessmentResponse,
    QualityCheckResponse,
)
from app.services.quality_assessment_service import QualityAssessmentService

router = APIRouter(prefix="/api/v1/photos", tags=["Quality Assessment"])


@router.post("/{photo_id}/assess-quality", response_model=QualityAssessmentResponse)
async def assess_quality(photo_id: int, db: Session = Depends(get_db)):
    """
    写真の品質を評価

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        QualityAssessmentResponse: 品質評価結果

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
        # S3から画像ダウンロード
        service = QualityAssessmentService()
        s3_bucket = "construction-photos"  # TODO: 環境変数化
        s3_key = photo.s3_key

        image_data = service.download_image_from_s3(bucket=s3_bucket, key=s3_key)

        # 品質評価
        result = service.assess_quality(image_data)

        # データベースに保存
        if photo.photo_metadata is None:
            photo.photo_metadata = {}

        photo.photo_metadata["quality"] = {
            "sharpness": result["sharpness"],
            "brightness": result["brightness"],
            "contrast": result["contrast"],
            "quality_score": result["quality_score"],
            "quality_grade": result["quality_grade"],
            "issues": result["issues"],
            "recommendations": result["recommendations"],
        }

        db.commit()
        db.refresh(photo)

        return QualityAssessmentResponse(
            photo_id=photo_id,
            sharpness=result["sharpness"],
            brightness=result["brightness"],
            contrast=result["contrast"],
            quality_score=result["quality_score"],
            quality_grade=result["quality_grade"],
            issues=result["issues"],
            recommendations=result["recommendations"],
            status="completed",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"品質評価に失敗しました: {str(e)}"
        )


@router.get("/{photo_id}/quality", response_model=QualityCheckResponse)
async def get_quality(photo_id: int, db: Session = Depends(get_db)):
    """
    写真の品質情報を取得

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        QualityCheckResponse: 品質情報

    Raises:
        HTTPException: 写真が見つからない、または品質未評価の場合
    """
    # 写真取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    # 品質情報取得
    if photo.photo_metadata is None or "quality" not in photo.photo_metadata:
        raise HTTPException(
            status_code=404, detail="品質評価が実行されていません。先に評価してください。"
        )

    quality_data = photo.photo_metadata["quality"]

    return QualityCheckResponse(
        photo_id=photo_id,
        quality_score=quality_data["quality_score"],
        quality_grade=quality_data["quality_grade"],
        status="exists",
    )
