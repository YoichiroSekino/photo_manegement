"""
検索APIルーター
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.database.database import get_db
from app.database.models import Photo, User
from app.schemas.search import SearchResponse
from app.schemas.photo import PhotoResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/v1/photos", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_photos(
    keyword: Optional[str] = Query(None, description="キーワード検索"),
    work_type: Optional[str] = Query(None, description="工種フィルタ"),
    work_kind: Optional[str] = Query(None, description="種別フィルタ"),
    major_category: Optional[str] = Query(None, description="写真大分類フィルタ"),
    photo_type: Optional[str] = Query(None, description="写真区分フィルタ"),
    date_from: Optional[str] = Query(None, description="撮影日開始（YYYY-MM-DD）"),
    date_to: Optional[str] = Query(None, description="撮影日終了（YYYY-MM-DD）"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    写真を検索（マルチテナント対応）

    Args:
        keyword: キーワード（ファイル名、タイトル、説明から検索）
        work_type: 工種
        work_kind: 種別
        major_category: 写真大分類
        photo_type: 写真区分
        date_from: 撮影日開始
        date_to: 撮影日終了
        page: ページ番号
        page_size: ページサイズ
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        検索結果（自組織のみ）
    """
    # テナントフィルタを適用
    query = db.query(Photo).filter(
        Photo.organization_id == current_user.organization_id
    )

    # キーワード検索（全文検索）
    if keyword:
        # データベースの種類を判定
        db_dialect = db.bind.dialect.name

        if db_dialect == "postgresql":
            # PostgreSQL: TSVectorを使った全文検索（高速）
            ts_query = func.plainto_tsquery("simple", keyword)
            query = query.filter(Photo.search_vector.op("@@")(ts_query))
            # 関連度順にソート
            query = query.order_by(func.ts_rank(Photo.search_vector, ts_query).desc())
        else:
            # SQLite/その他: LIKE検索にフォールバック
            search_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    Photo.file_name.like(search_pattern),
                    Photo.title.like(search_pattern),
                    Photo.description.like(search_pattern),
                    Photo.work_type.like(search_pattern),
                    Photo.work_kind.like(search_pattern),
                )
            )

    # 工種フィルタ
    if work_type:
        query = query.filter(Photo.work_type == work_type)

    # 種別フィルタ
    if work_kind:
        query = query.filter(Photo.work_kind == work_kind)

    # 写真大分類フィルタ
    if major_category:
        query = query.filter(Photo.major_category == major_category)

    # 写真区分フィルタ
    if photo_type:
        query = query.filter(Photo.photo_type == photo_type)

    # 日付範囲フィルタ
    if date_from:
        date_from_dt = datetime.fromisoformat(date_from)
        query = query.filter(Photo.shooting_date >= date_from_dt)

    if date_to:
        date_to_dt = datetime.fromisoformat(date_to)
        # 日付の終わりまで含める（23:59:59）
        from datetime import timedelta

        date_to_end = date_to_dt + timedelta(days=1, seconds=-1)
        query = query.filter(Photo.shooting_date <= date_to_end)

    # 総数を取得
    total = query.count()

    # ページネーション
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size

    # データ取得（キーワードがない場合は作成日時降順）
    if not keyword:
        query = query.order_by(Photo.created_at.desc())

    photos = query.offset(skip).limit(page_size).all()

    return SearchResponse(
        items=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
