"""
写真管理APIルーター
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os

from app.database.database import get_db
from app.database.models import Photo, User
from app.schemas.photo import PhotoCreate, PhotoResponse, PhotoListResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])


class PresignedUrlRequest(BaseModel):
    """Presigned URL リクエスト"""

    fileName: str
    fileSize: int
    mimeType: str


class PresignedUrlResponse(BaseModel):
    """Presigned URL レスポンス"""

    presignedUrl: str
    key: str
    bucket: str
    expiresIn: int


@router.post("/upload", response_model=PresignedUrlResponse)
async def generate_presigned_url(
    request: PresignedUrlRequest, current_user: User = Depends(get_current_active_user)
):
    """
    S3アップロード用のPresigned URLを生成する（マルチテナント対応）

    Args:
        request: ファイル情報
        current_user: 現在の認証済みユーザー

    Returns:
        Presigned URLとメタデータ

    Raises:
        HTTPException: Presigned URL生成に失敗した場合
    """
    try:
        # S3クライアント初期化
        s3_client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "ap-northeast-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        bucket_name = os.getenv("S3_BUCKET_NAME", "construction-photos-dev")

        # S3キーを生成（組織ID/写真/タイムスタンプ_ファイル名）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = (
            request.fileName.split(".")[-1] if "." in request.fileName else ""
        )
        s3_key = f"organizations/{current_user.organization_id}/photos/{timestamp}_{request.fileName}"

        # Presigned URL生成（有効期限: 15分）
        expires_in = 900  # 15分
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key,
                "ContentType": request.mimeType,
            },
            ExpiresIn=expires_in,
        )

        return PresignedUrlResponse(
            presignedUrl=presigned_url,
            key=s3_key,
            bucket=bucket_name,
            expiresIn=expires_in,
        )

    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Presigned URL生成に失敗しました: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"予期しないエラーが発生しました: {str(e)}",
        )


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    photo: PhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    写真を作成する（マルチテナント対応）

    Args:
        photo: 写真作成データ
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        作成された写真データ
    """
    db_photo = Photo(
        organization_id=current_user.organization_id,  # 自動的に組織IDを設定
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
    current_user: User = Depends(get_current_active_user),
):
    """
    写真一覧を取得する（ページネーション付き・マルチテナント対応）

    Args:
        page: ページ番号（1から開始）
        page_size: 1ページあたりのアイテム数
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        写真一覧とメタデータ（自組織のみ）
    """
    # テナントフィルタ適用
    query = db.query(Photo).filter(
        Photo.organization_id == current_user.organization_id
    )

    # 総数を取得
    total = query.count()

    # ページネーション計算
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size

    # データ取得
    photos = query.offset(skip).limit(page_size).all()

    return PhotoListResponse(
        items=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    写真詳細を取得する（マルチテナント対応）

    Args:
        photo_id: 写真ID
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        写真詳細データ（自組織のみ）

    Raises:
        HTTPException: 写真が見つからない、または他組織の写真の場合
    """
    photo = (
        db.query(Photo)
        .filter(
            Photo.id == photo_id,
            Photo.organization_id == current_user.organization_id,  # テナントフィルタ
        )
        .first()
    )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"写真が見つかりません（ID: {photo_id}）",
        )

    return photo
