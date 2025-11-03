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
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get dashboard statistics.

    Args:
        project_id: Optional project ID to filter statistics

    Returns:
        - total_photos: Total number of photos
        - today_uploads: Photos uploaded today
        - this_week_uploads: Photos uploaded this week
        - duplicates_count: Number of duplicate groups
        - quality_issues_count: Photos with quality score < 50
        - category_distribution: Photo count by major category
    """
    # Base query with organization filter
    base_query = db.query(Photo).filter(Photo.organization_id == current_user.organization_id)

    # Add project filter if provided
    if project_id is not None:
        base_query = base_query.filter(Photo.project_id == project_id)

    # Total photos
    total_photos = base_query.count() or 0

    # Today's uploads
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_uploads = (
        base_query.filter(Photo.created_at >= today_start).count() or 0
    )

    # This week's uploads
    week_start = today_start - timedelta(days=today_start.weekday())
    this_week_uploads = (
        base_query.filter(Photo.created_at >= week_start).count() or 0
    )

    # Duplicate groups count
    duplicates_count = (
        base_query.filter(Photo.duplicate_group_id.isnot(None))
        .with_entities(func.count(func.distinct(Photo.duplicate_group_id)))
        .scalar()
        or 0
    )

    # Quality issues (quality score < 50)
    quality_issues_count = (
        base_query.filter(Photo.quality_score < 50).count() or 0
    )

    # Category distribution
    category_distribution = (
        base_query.with_entities(Photo.major_category, func.count(Photo.id))
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
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get recently uploaded photos.

    Args:
        limit: Number of photos to return (default: 6)
        project_id: Optional project ID to filter photos

    Returns:
        List of recent photos with basic metadata
    """
    # Base query with organization filter
    query = db.query(Photo).filter(Photo.organization_id == current_user.organization_id)

    # Add project filter if provided
    if project_id is not None:
        query = query.filter(Photo.project_id == project_id)

    photos = (
        query
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
