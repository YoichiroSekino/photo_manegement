"""
写真管理APIルーター
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os
import shutil

from app.database.database import get_db
from app.database.models import Photo, User
from app.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse, PhotoListResponse
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
    # 開発環境またはAWS認証情報が未設定の場合はモックURLを返す
    use_mock = os.getenv("USE_MOCK_S3", "true").lower() == "true"

    if use_mock or not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        # モックPresigned URL（開発環境専用）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        s3_key = f"organizations/{current_user.organization_id}/photos/{timestamp}_{request.fileName}"
        bucket_name = "construction-photos-dev"

        return PresignedUrlResponse(
            presignedUrl=f"https://mock-s3-url.example.com/{bucket_name}/{s3_key}",
            key=s3_key,
            bucket=bucket_name,
            expiresIn=900,
        )

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


@router.post("/mock-upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def mock_upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    開発環境用：ファイルをローカルに保存して写真レコードを作成

    Args:
        file: アップロードファイル
        current_user: 現在の認証済みユーザー
        db: データベースセッション

    Returns:
        作成された写真データ
    """
    # ファイルをローカルに保存
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    local_filename = f"{timestamp}_{file.filename}"

    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    file_path = os.path.join(uploads_dir, local_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 写真レコードを作成
    s3_key = f"organizations/{current_user.organization_id}/photos/{local_filename}"

    db_photo = Photo(
        organization_id=current_user.organization_id,
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type or "image/jpeg",
        s3_key=s3_key,
        s3_url=f"http://localhost:8000/static/uploads/{local_filename}",  # ローカルURL
    )

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    return db_photo


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
    # モックモードの場合、ローカルURLを使用
    s3_url = photo.s3_url
    if os.getenv("USE_MOCK_S3", "true").lower() == "true" and not s3_url:
        # S3キーからローカルファイル名を抽出
        filename = photo.s3_key.split("/")[-1] if photo.s3_key else photo.file_name
        s3_url = f"http://localhost:8000/static/uploads/{filename}"

    db_photo = Photo(
        organization_id=current_user.organization_id,  # 自動的に組織IDを設定
        project_id=photo.project_id,  # プロジェクトID
        file_name=photo.file_name,
        file_size=photo.file_size,
        mime_type=photo.mime_type,
        s3_key=photo.s3_key,
        s3_url=s3_url,
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
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    写真一覧を取得する（ページネーション付き・マルチテナント対応）

    Args:
        page: ページ番号（1から開始）
        page_size: 1ページあたりのアイテム数
        project_id: プロジェクトIDでフィルタ（オプション）
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        写真一覧とメタデータ（自組織のみ）
    """
    # テナントフィルタ適用
    query = db.query(Photo).filter(
        Photo.organization_id == current_user.organization_id
    )

    # プロジェクトフィルタ（オプション）
    if project_id is not None:
        query = query.filter(Photo.project_id == project_id)

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


@router.patch("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    写真情報を更新する（マルチテナント対応）

    Args:
        photo_id: 写真ID
        photo_update: 更新データ
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        更新された写真データ

    Raises:
        HTTPException: 写真が見つからない、または他組織の写真の場合
    """
    photo = (
        db.query(Photo)
        .filter(
            Photo.id == photo_id,
            Photo.organization_id == current_user.organization_id,
        )
        .first()
    )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"写真が見つかりません（ID: {photo_id}）",
        )

    # 更新可能なフィールドを更新
    if photo_update.project_id is not None:
        photo.project_id = photo_update.project_id
    if photo_update.title is not None:
        photo.title = photo_update.title
    if photo_update.description is not None:
        photo.description = photo_update.description
    if photo_update.shooting_date is not None:
        photo.shooting_date = photo_update.shooting_date
    if photo_update.major_category is not None:
        photo.major_category = photo_update.major_category
    if photo_update.photo_type is not None:
        photo.photo_type = photo_update.photo_type
    if photo_update.work_type is not None:
        photo.work_type = photo_update.work_type
    if photo_update.tags is not None:
        photo.tags = photo_update.tags

    db.commit()
    db.refresh(photo)

    return photo
