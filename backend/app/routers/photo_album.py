"""
工事写真帳生成 APIルーター
"""

import tempfile
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo
from app.schemas.photo_album import (
    PhotoAlbumGenerationRequest,
    PhotoAlbumGenerationResponse,
    LayoutType as LayoutTypeSchema,
)
from app.services.photo_album_generator import PhotoAlbumGenerator, LayoutType

router = APIRouter(prefix="/api/v1/photo-album", tags=["photo-album"])


@router.post("/generate-pdf", response_model=PhotoAlbumGenerationResponse)
async def generate_photo_album_pdf(
    request: PhotoAlbumGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    PDF写真帳を生成

    Args:
        request: 写真帳生成リクエスト
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
    for photo in photos:
        photo_dict = {
            "id": photo.id,
            "file_name": photo.file_name,
            "title": photo.title or "",
            "shooting_date": (
                photo.shooting_date.isoformat() if photo.shooting_date else ""
            ),
            "major_category": photo.major_category or "",
            "photo_type": photo.photo_type or "",
            "work_type": photo.work_type or "",
            "work_kind": photo.work_kind or "",
            "work_detail": photo.work_detail or "",
            "image_data": None,  # TODO: S3から画像データ取得
        }
        photo_dicts.append(photo_dict)

    # 写真帳生成サービス
    album_generator = PhotoAlbumGenerator()

    # 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "photo_album.pdf")

    try:
        # レイアウトタイプ変換
        layout_type_map = {
            LayoutTypeSchema.STANDARD: LayoutType.STANDARD,
            LayoutTypeSchema.COMPACT: LayoutType.COMPACT,
            LayoutTypeSchema.DETAILED: LayoutType.DETAILED,
        }
        layout_type = layout_type_map[request.layout_type]

        # 表紙データ変換
        cover_data = None
        if request.cover_data:
            cover_data = {
                "project_name": request.cover_data.project_name,
                "contractor": request.cover_data.contractor,
                "period_from": request.cover_data.period_from,
                "period_to": request.cover_data.period_to,
                "location": request.cover_data.location,
            }

        # PDF生成
        result = album_generator.generate_pdf(
            photos=photo_dicts,
            output_path=output_path,
            layout_type=layout_type,
            cover_data=cover_data,
            add_page_numbers=request.add_page_numbers,
            header_text=request.header_text,
            footer_text=request.footer_text,
        )

        if not result["success"]:
            return PhotoAlbumGenerationResponse(
                success=False,
                pdf_path=None,
                download_url=None,
                total_pages=0,
                total_photos=0,
                file_size=None,
                errors=result["errors"],
                status="error",
            )

        return PhotoAlbumGenerationResponse(
            success=True,
            pdf_path=result["pdf_path"],
            download_url=f"/api/v1/photo-album/download?path={result['pdf_path']}",
            total_pages=result["total_pages"],
            total_photos=result["total_photos"],
            file_size=result.get("file_size"),
            errors=[],
            status="success",
        )

    except Exception as e:
        return PhotoAlbumGenerationResponse(
            success=False,
            pdf_path=None,
            download_url=None,
            total_pages=0,
            total_photos=0,
            file_size=None,
            errors=[str(e)],
            status="error",
        )


@router.get("/download")
async def download_photo_album(path: str):
    """
    写真帳PDFをダウンロード

    Args:
        path: ファイルパス

    Returns:
        ファイルレスポンス
    """
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename="photo_album.pdf",
    )
