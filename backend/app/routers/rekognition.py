"""
Amazon Rekognition 画像分類 API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo, User
from app.schemas.rekognition import (
    ClassificationResponse,
    ClassificationResultResponse,
    ImageLabelResponse,
)
from app.services.rekognition_service import RekognitionService
from app.auth.dependencies import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/api/v1/photos", tags=["Rekognition"])


@router.post("/{photo_id}/classify", response_model=ClassificationResponse)
async def classify_image(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    画像分類を実行（マルチテナント対応）

    Args:
        photo_id: 写真ID
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        ClassificationResponse: 分類結果（自組織のみ）

    Raises:
        HTTPException: 写真が見つからない、または他組織の写真の場合
    """
    # 写真取得（テナントフィルタ適用）
    photo = (
        db.query(Photo)
        .filter(
            Photo.id == photo_id, Photo.organization_id == current_user.organization_id
        )
        .first()
    )
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    # Rekognitionサービス初期化
    rekognition_service = RekognitionService(confidence_threshold=70.0)

    # S3情報取得
    s3_bucket = settings.S3_BUCKET
    s3_key = photo.s3_key

    try:
        # ラベル検出
        labels = rekognition_service.detect_labels_from_image(
            s3_bucket=s3_bucket, s3_key=s3_key
        )

        # カテゴリ分類
        categorized = rekognition_service.categorize_construction_labels(labels)

        # サマリー作成
        summary = rekognition_service.create_image_label_summary(labels)

        # データベースに保存
        if photo.photo_metadata is None:
            photo.photo_metadata = {}

        photo.photo_metadata["rekognition_labels"] = [
            {
                "name": label["Name"],
                "confidence": label["Confidence"],
                "parents": label["Parents"],
            }
            for label in labels
        ]
        photo.photo_metadata["rekognition_categorized"] = categorized
        photo.photo_metadata["rekognition_summary"] = summary

        db.commit()
        db.refresh(photo)

        # レスポンス作成
        return ClassificationResponse(
            photo_id=photo_id,
            status="completed",
            labels=[
                ImageLabelResponse(
                    name=label["Name"],
                    confidence=label["Confidence"],
                    parents=label["Parents"],
                )
                for label in labels
            ],
            categorized_labels=categorized,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"画像分類処理に失敗しました: {str(e)}"
        )


@router.get("/{photo_id}/classification", response_model=ClassificationResultResponse)
async def get_classification_result(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    画像分類結果を取得（マルチテナント対応）

    Args:
        photo_id: 写真ID
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        ClassificationResultResponse: 分類結果（自組織のみ）

    Raises:
        HTTPException: 写真が見つからない、または他組織の写真の場合
    """
    # 写真取得（テナントフィルタ適用）
    photo = (
        db.query(Photo)
        .filter(
            Photo.id == photo_id, Photo.organization_id == current_user.organization_id
        )
        .first()
    )
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    # メタデータから分類結果取得
    if photo.photo_metadata is None or "rekognition_labels" not in photo.photo_metadata:
        # 未処理
        return ClassificationResultResponse(
            photo_id=photo_id, status="not_processed", labels=[]
        )

    # 処理済み
    labels_data = photo.photo_metadata.get("rekognition_labels", [])
    categorized = photo.photo_metadata.get("rekognition_categorized")
    summary = photo.photo_metadata.get("rekognition_summary")

    return ClassificationResultResponse(
        photo_id=photo_id,
        status="completed",
        labels=[
            ImageLabelResponse(
                name=label["name"],
                confidence=label["confidence"],
                parents=label.get("parents", []),
            )
            for label in labels_data
        ],
        categorized_labels=categorized,
        summary=summary,
    )
