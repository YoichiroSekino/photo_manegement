"""Dashboard statistics router."""

from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Photo, User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get dashboard statistics.

    Returns:
        - total_photos: Total number of photos
        - today_uploads: Photos uploaded today
        - this_week_uploads: Photos uploaded this week
        - duplicates_count: Number of duplicate groups
        - quality_issues_count: Photos with quality score < 50
        - category_distribution: Photo count by major category
    """
    # Total photos
    total_photos = db.query(func.count(Photo.id)).scalar() or 0

    # Today's uploads
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_uploads = (
        db.query(func.count(Photo.id))
        .filter(Photo.created_at >= today_start)
        .scalar()
        or 0
    )

    # This week's uploads
    week_start = today_start - timedelta(days=today_start.weekday())
    this_week_uploads = (
        db.query(func.count(Photo.id))
        .filter(Photo.created_at >= week_start)
        .scalar()
        or 0
    )

    # Duplicate groups count
    duplicates_count = (
        db.query(func.count(func.distinct(Photo.duplicate_group_id)))
        .filter(Photo.duplicate_group_id.isnot(None))
        .scalar()
        or 0
    )

    # Quality issues (quality score < 50)
    quality_issues_count = (
        db.query(func.count(Photo.id))
        .filter(Photo.quality_score < 50)
        .scalar()
        or 0
    )

    # Category distribution
    category_distribution = (
        db.query(Photo.major_category, func.count(Photo.id))
        .group_by(Photo.major_category)
        .all()
    )
    category_dist_dict = {
        category or "未分類": count for category, count in category_distribution
    }

    return {
        "total_photos": total_photos,
        "today_uploads": today_uploads,
        "this_week_uploads": this_week_uploads,
        "duplicates_count": duplicates_count,
        "quality_issues_count": quality_issues_count,
        "category_distribution": category_dist_dict,
    }


@router.get("/recent-photos")
async def get_recent_photos(
    limit: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get recently uploaded photos.

    Args:
        limit: Number of photos to return (default: 6)

    Returns:
        List of recent photos with basic metadata
    """
    photos = (
        db.query(Photo)
        .order_by(Photo.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": photo.id,
            "file_name": photo.file_name,
            "s3_key": photo.s3_key,
            "s3_url": photo.s3_url,
            "title": photo.title,
            "major_category": photo.major_category,
            "shooting_date": photo.shooting_date,
            "quality_score": photo.quality_score,
            "created_at": photo.created_at,
        }
        for photo in photos
    ]
