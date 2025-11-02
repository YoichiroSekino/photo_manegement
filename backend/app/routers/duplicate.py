"""
重複写真検出 API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.duplicate import (
    DuplicateDetectionResponse,
    DuplicateGroupResponse,
    DuplicatePhotoInfo,
    CalculateHashResponse,
)
from app.services.duplicate_detection_service import DuplicateDetectionService

router = APIRouter(prefix="/api/v1/photos", tags=["Duplicate Detection"])


@router.post("/detect-duplicates", response_model=DuplicateDetectionResponse)
async def detect_duplicates(
    similarity_threshold: float = Query(90.0, ge=70.0, le=100.0),
    db: Session = Depends(get_db),
):
    """
    全写真から重複を検出

    Args:
        similarity_threshold: 類似度閾値（70-100%）
        db: データベースセッション

    Returns:
        DuplicateDetectionResponse: 重複検出結果
    """
    # データベースから全写真取得（pHashが存在するもののみ）
    photos = (
        db.query(Photo)
        .filter(Photo.photo_metadata.isnot(None))
        .filter(Photo.photo_metadata["phash"].isnot(None))
        .all()
    )

    if len(photos) < 2:
        return DuplicateDetectionResponse(
            total_photos=len(photos),
            duplicate_groups=[],
            summary={
                "total_groups": 0,
                "total_duplicate_photos": 0,
                "avg_similarity": 0.0,
                "largest_group_size": 0,
            },
        )

    # 写真リストを辞書形式に変換
    photo_dicts = [
        {
            "id": photo.id,
            "phash": photo.photo_metadata.get("phash"),
            "file_name": photo.file_name,
        }
        for photo in photos
        if photo.photo_metadata.get("phash")
    ]

    # 重複検出サービス
    service = DuplicateDetectionService(similarity_threshold=similarity_threshold)
    duplicate_groups = service.find_duplicates_in_photos(photo_dicts)
    summary = service.create_duplicate_summary(duplicate_groups)

    # レスポンス作成
    groups_response = []
    for idx, group in enumerate(duplicate_groups, start=1):
        photos_info = [
            DuplicatePhotoInfo(
                id=photo["id"],
                file_name=photo.get("file_name", ""),
                phash=photo["phash"],
            )
            for photo in group.photos
        ]

        groups_response.append(
            DuplicateGroupResponse(
                group_id=idx,
                photos=photos_info,
                avg_similarity=group.avg_similarity,
                photo_count=len(group.photos),
            )
        )

    return DuplicateDetectionResponse(
        total_photos=len(photos),
        duplicate_groups=groups_response,
        summary=summary,
    )


@router.post("/{photo_id}/calculate-hash", response_model=CalculateHashResponse)
async def calculate_hash(photo_id: int, db: Session = Depends(get_db)):
    """
    写真のpHashを計算

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        CalculateHashResponse: 計算結果

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
        service = DuplicateDetectionService()
        s3_bucket = "construction-photos"  # TODO: 環境変数化
        s3_key = photo.s3_key

        image_data = service.download_image_from_s3(bucket=s3_bucket, key=s3_key)

        # pHash計算
        phash = service.calculate_phash(image_data)

        # データベースに保存
        if photo.photo_metadata is None:
            photo.photo_metadata = {}

        photo.photo_metadata["phash"] = phash
        db.commit()
        db.refresh(photo)

        return CalculateHashResponse(photo_id=photo_id, phash=phash, status="completed")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"ハッシュ計算に失敗しました: {str(e)}"
        )


@router.get("/{photo_id}/hash", response_model=CalculateHashResponse)
async def get_hash(photo_id: int, db: Session = Depends(get_db)):
    """
    写真のpHashを取得

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        CalculateHashResponse: ハッシュ情報

    Raises:
        HTTPException: 写真が見つからない、またはハッシュ未計算の場合
    """
    # 写真取得
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(
            status_code=404, detail=f"写真が見つかりません（ID: {photo_id}）"
        )

    # pHash取得
    if photo.photo_metadata is None or "phash" not in photo.photo_metadata:
        raise HTTPException(
            status_code=404, detail="pHashが計算されていません。先に計算してください。"
        )

    phash = photo.photo_metadata["phash"]

    return CalculateHashResponse(photo_id=photo_id, phash=phash, status="exists")
