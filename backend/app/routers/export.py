"""
エクスポート APIルーター
"""

import tempfile
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.export import (
    ExportRequest,
    ExportResponse,
    ExportValidationResponse,
    FileRenameInfo,
)
from app.services.export_service import ExportService
from app.services.photo_xml_generator import PhotoXMLGenerator

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.post("/package", response_model=ExportResponse)
async def export_package(
    request: ExportRequest,
    db: Session = Depends(get_db),
):
    """
    電子納品パッケージをエクスポート

    Args:
        request: エクスポートリクエスト
        db: データベースセッション

    Returns:
        エクスポート結果
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
        photo_dicts.append(photo_dict)

    # PHOTO.XML生成
    xml_generator = PhotoXMLGenerator()
    xml_content = xml_generator.generate_xml(photo_dicts, pretty_print=True)

    # エクスポートサービス
    export_service = ExportService()

    # 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp()

    try:
        # エクスポートパッケージ作成
        result = export_service.export_package(
            photos=photo_dicts,
            xml_content=xml_content,
            export_dir=temp_dir,
            project_name=request.project_name,
        )

        if not result["success"]:
            return ExportResponse(
                success=False,
                zip_path=None,
                download_url=None,
                total_photos=0,
                file_size=None,
                file_renames=[],
                errors=result["errors"],
                status="error",
            )

        # ファイルリネーム情報生成
        file_renames = export_service.rename_multiple_photos(photo_dicts)
        file_rename_infos = [
            FileRenameInfo(**rename) for rename in file_renames
        ]

        return ExportResponse(
            success=True,
            zip_path=result["zip_path"],
            download_url=f"/api/v1/export/download?path={result['zip_path']}",
            total_photos=result["total_photos"],
            file_size=result.get("file_size"),
            file_renames=file_rename_infos,
            errors=[],
            status="success",
        )

    except Exception as e:
        return ExportResponse(
            success=False,
            zip_path=None,
            download_url=None,
            total_photos=0,
            file_size=None,
            file_renames=[],
            errors=[str(e)],
            status="error",
        )


@router.post("/validate", response_model=ExportValidationResponse)
async def validate_export(
    request: ExportRequest,
    db: Session = Depends(get_db),
):
    """
    エクスポート前にデータをバリデーション

    Args:
        request: エクスポートリクエスト
        db: データベースセッション

    Returns:
        バリデーション結果
    """
    # 写真データ取得
    photos = db.query(Photo).filter(Photo.id.in_(request.photo_ids)).all()

    if not photos:
        return ExportValidationResponse(
            is_valid=False,
            total_photos=0,
            errors=["指定された写真が見つかりません"],
            warnings=[],
        )

    if len(photos) != len(request.photo_ids):
        return ExportValidationResponse(
            is_valid=False,
            total_photos=len(photos),
            errors=[
                f"一部の写真が見つかりません（指定: {len(request.photo_ids)}件, 取得: {len(photos)}件）"
            ],
            warnings=[],
        )

    export_service = ExportService()
    xml_generator = PhotoXMLGenerator()
    errors = []
    warnings = []

    # 写真データをディクショナリに変換
    photo_dicts = []
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
        photo_dicts.append(photo_dict)

        # XML用データバリデーション
        xml_errors = xml_generator.validate_photo_data(photo_dict)
        if xml_errors:
            errors.extend([f"写真ID {photo.id}: {error}" for error in xml_errors])

        # 警告チェック
        if not photo.title:
            warnings.append(f"写真ID {photo.id}: タイトルが未設定です")

        if not photo.photo_metadata or not photo.photo_metadata.get("ocr_result"):
            warnings.append(f"写真ID {photo.id}: OCRデータが未処理です")

    # ファイル名重複チェック
    duplicates = export_service.check_filename_duplication(photo_dicts)
    if duplicates:
        errors.extend([f"ファイル名が重複しています: {dup}" for dup in duplicates])

    # 推定ファイルサイズ（概算: 1枚あたり2MB）
    estimated_file_size = len(photos) * 2 * 1024 * 1024

    is_valid = len(errors) == 0

    return ExportValidationResponse(
        is_valid=is_valid,
        total_photos=len(photos),
        errors=errors,
        warnings=warnings,
        estimated_file_size=estimated_file_size,
    )


@router.get("/download")
async def download_export_file(path: str):
    """
    エクスポートファイルをダウンロード

    Args:
        path: ファイルパス

    Returns:
        ファイルレスポンス
    """
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    return FileResponse(
        path=path,
        media_type="application/zip",
        filename=os.path.basename(path),
    )
