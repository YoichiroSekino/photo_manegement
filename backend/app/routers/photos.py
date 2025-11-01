"""
写真管理APIルーター
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.photo import PhotoCreate, PhotoResponse, PhotoListResponse

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(photo: PhotoCreate, db: Session = Depends(get_db)):
    """
    写真を作成する

    Args:
        photo: 写真作成データ
        db: データベースセッション

    Returns:
        作成された写真データ
    """
    db_photo = Photo(
        file_name=photo.file_name,
        file_size=photo.file_size,
        mime_type=photo.mime_type,
        s3_key=photo.s3_key,
        title=photo.title,
        description=photo.description,
        shooting_date=photo.shooting_date,
        latitude=photo.latitude,
        longitude=photo.longitude,
        location_address=photo.location_address,
        major_category=photo.major_category,
        photo_type=photo.photo_type,
        work_type=photo.work_type,
        work_kind=photo.work_kind,
        work_detail=photo.work_detail,
        tags=photo.tags,
        photo_metadata=photo.metadata,
    )

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    return db_photo


@router.get("", response_model=PhotoListResponse)
async def get_photos(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    写真一覧を取得する（ページネーション付き）

    Args:
        page: ページ番号（1から開始）
        page_size: 1ページあたりのアイテム数
        db: データベースセッション

    Returns:
        写真一覧とメタデータ
    """
    # 総数を取得
    total = db.query(Photo).count()

    # ページネーション計算
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size

    # データ取得
    photos = db.query(Photo).offset(skip).limit(page_size).all()

    return PhotoListResponse(
        items=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    写真詳細を取得する

    Args:
        photo_id: 写真ID
        db: データベースセッション

    Returns:
        写真詳細データ

    Raises:
        HTTPException: 写真が見つからない場合
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"写真が見つかりません（ID: {photo_id}）",
        )

    return photo
