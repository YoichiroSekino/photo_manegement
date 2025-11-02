"""
PHOTO.XML生成 APIルーター
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.photo_xml import (
    PhotoXMLGenerationRequest,
    PhotoXMLGenerationResponse,
    PhotoXMLValidationResponse,
)
from app.services.photo_xml_generator import PhotoXMLGenerator

router = APIRouter(prefix="/api/v1/photo-xml", tags=["photo-xml"])


@router.post("/generate", response_model=PhotoXMLGenerationResponse)
async def generate_photo_xml(
    request: PhotoXMLGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    PHOTO.XMLを生成

    Args:
        request: XML生成リクエスト
        db: データベースセッション

    Returns:
        生成結果
    """
    # 写真データ取得
    photos = db.query(Photo).filter(Photo.id.in_(request.photo_ids)).all()

    if not photos:
        raise HTTPException(status_code=404, detail="指定された写真が見つかりません")

    if len(photos) != len(request.photo_ids):
        raise HTTPException(
            status_code=400,
            detail=f"一部の写真が見つかりません（指定: {len(request.photo_ids)}件, 取得: {len(photos)}件）",
        )

    # 写真データをディクショナリに変換
    photo_dicts = []
    validation_errors = []

    xml_generator = PhotoXMLGenerator()

    for photo in photos:
        photo_dict = {
            "id": photo.id,
            "file_name": photo.file_name,
            "title": photo.title or "",
            "shooting_date": photo.shooting_date.isoformat() if photo.shooting_date else "",
            "major_category": photo.major_category or "",
            "photo_type": photo.photo_type or "",
            "work_type": photo.work_type or "",
            "work_kind": photo.work_kind or "",
            "work_detail": photo.work_detail or "",
            "photo_metadata": photo.photo_metadata or {},
        }

        # プロジェクト情報を追加（最初の写真のみ）
        if len(photo_dicts) == 0 and request.project_name:
            photo_dict["project_name"] = request.project_name
        if len(photo_dicts) == 0 and request.contractor:
            photo_dict["contractor"] = request.contractor

        # データバリデーション
        errors = xml_generator.validate_photo_data(photo_dict)
        if errors:
            validation_errors.extend(
                [f"写真ID {photo.id}: {error}" for error in errors]
            )

        photo_dicts.append(photo_dict)

    # XML生成
    xml_content = xml_generator.generate_xml(photo_dicts, pretty_print=True)

    # ファイルサイズ計算（Shift_JISエンコード後）
    file_size = len(xml_content.encode("shift_jis"))

    # ステータス決定
    status = "success" if not validation_errors else "success_with_warnings"

    return PhotoXMLGenerationResponse(
        total_photos=len(photo_dicts),
        xml_content=xml_content,
        file_size=file_size,
        validation_errors=validation_errors,
        status=status,
    )


@router.post("/validate", response_model=PhotoXMLValidationResponse)
async def validate_photo_xml(
    request: PhotoXMLGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    PHOTO.XML生成前にデータをバリデーション

    Args:
        request: XML生成リクエスト
        db: データベースセッション

    Returns:
        バリデーション結果
    """
    # 写真データ取得
    photos = db.query(Photo).filter(Photo.id.in_(request.photo_ids)).all()

    if not photos:
        return PhotoXMLValidationResponse(
            is_valid=False,
            errors=["指定された写真が見つかりません"],
            warnings=[],
        )

    if len(photos) != len(request.photo_ids):
        return PhotoXMLValidationResponse(
            is_valid=False,
            errors=[
                f"一部の写真が見つかりません（指定: {len(request.photo_ids)}件, 取得: {len(photos)}件）"
            ],
            warnings=[],
        )

    xml_generator = PhotoXMLGenerator()
    errors = []
    warnings = []

    for photo in photos:
        photo_dict = {
            "id": photo.id,
            "file_name": photo.file_name,
            "title": photo.title or "",
            "shooting_date": photo.shooting_date.isoformat() if photo.shooting_date else "",
            "major_category": photo.major_category or "",
            "photo_type": photo.photo_type or "",
            "work_type": photo.work_type or "",
            "work_kind": photo.work_kind or "",
            "work_detail": photo.work_detail or "",
            "photo_metadata": photo.photo_metadata or {},
        }

        # データバリデーション
        photo_errors = xml_generator.validate_photo_data(photo_dict)
        if photo_errors:
            errors.extend([f"写真ID {photo.id}: {error}" for error in photo_errors])

        # 警告チェック
        # OCRデータがない場合
        if not photo.photo_metadata or not photo.photo_metadata.get("ocr_result"):
            warnings.append(f"写真ID {photo.id}: OCRデータが未処理です")

        # 分類データがない場合
        if not photo.photo_metadata or not photo.photo_metadata.get("classification"):
            warnings.append(f"写真ID {photo.id}: 分類データが未処理です")

    is_valid = len(errors) == 0

    return PhotoXMLValidationResponse(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
    )
