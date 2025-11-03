"""
プロジェクト管理API
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database.database import get_db
from app.database.models import Project, User, Photo
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectStatsResponse,
)
from app.schemas.photo import PhotoResponse

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクトを作成

    Args:
        project_data: プロジェクト作成データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ProjectResponse: 作成されたプロジェクト情報
    """
    # Create new project for user's organization
    new_project = Project(
        organization_id=current_user.organization_id,
        name=project_data.name,
        description=project_data.description,
        client_name=project_data.client_name,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Get photo count
    photo_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == new_project.id
    ).scalar()

    response = ProjectResponse(
        id=new_project.id,
        organization_id=new_project.organization_id,
        name=new_project.name,
        description=new_project.description,
        client_name=new_project.client_name,
        start_date=new_project.start_date,
        end_date=new_project.end_date,
        photo_count=photo_count or 0,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
    )

    return response


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクト一覧を取得（現在の組織のみ）

    Args:
        skip: スキップする件数
        limit: 取得する件数
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        List[ProjectResponse]: プロジェクト一覧
    """
    # Filter by organization for tenant isolation
    query = db.query(Project).filter(
        Project.organization_id == current_user.organization_id
    )

    # Order by created_at descending
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    # Build response with photo counts
    response = []
    for project in projects:
        photo_count = db.query(func.count(Photo.id)).filter(
            Photo.project_id == project.id
        ).scalar()

        response.append(
            ProjectResponse(
                id=project.id,
                organization_id=project.organization_id,
                name=project.name,
                description=project.description,
                client_name=project.client_name,
                start_date=project.start_date,
                end_date=project.end_date,
                photo_count=photo_count or 0,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    return response


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクト詳細を取得

    Args:
        project_id: プロジェクトID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ProjectResponse: プロジェクト詳細

    Raises:
        HTTPException: プロジェクトが見つからない場合
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # Tenant isolation check
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="このプロジェクトにアクセスする権限がありません")

    # Get photo count
    photo_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project.id
    ).scalar()

    response = ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        name=project.name,
        description=project.description,
        client_name=project.client_name,
        start_date=project.start_date,
        end_date=project.end_date,
        photo_count=photo_count or 0,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )

    return response


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクト情報を更新

    Args:
        project_id: プロジェクトID
        project_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ProjectResponse: 更新されたプロジェクト情報

    Raises:
        HTTPException: プロジェクトが見つからない場合
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # Tenant isolation check
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="このプロジェクトにアクセスする権限がありません")

    # Update fields if provided
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.client_name is not None:
        project.client_name = project_data.client_name
    if project_data.start_date is not None:
        project.start_date = project_data.start_date
    if project_data.end_date is not None:
        project.end_date = project_data.end_date

    db.commit()
    db.refresh(project)

    # Get photo count
    photo_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project.id
    ).scalar()

    response = ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        name=project.name,
        description=project.description,
        client_name=project.client_name,
        start_date=project.start_date,
        end_date=project.end_date,
        photo_count=photo_count or 0,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )

    return response


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクトを削除

    写真が紐づいている場合は削除できません（RESTRICT動作）

    Args:
        project_id: プロジェクトID
        db: データベースセッション
        current_user: 現在のユーザー

    Raises:
        HTTPException: プロジェクトが見つからない、または写真が紐づいている場合
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # Tenant isolation check
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="このプロジェクトにアクセスする権限がありません")

    # Check if project has photos (RESTRICT behavior)
    photo_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project.id
    ).scalar()

    if photo_count and photo_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"このプロジェクトには{photo_count}枚の写真が紐づいているため削除できません。先に写真を削除または別のプロジェクトに移動してください。"
        )

    db.delete(project)
    db.commit()

    return None


@router.get("/{project_id}/photos", response_model=List[PhotoResponse])
async def get_project_photos(
    project_id: int,
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクトに紐づく写真一覧を取得

    Args:
        project_id: プロジェクトID
        skip: スキップする件数
        limit: 取得する件数
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        List[PhotoResponse]: 写真一覧

    Raises:
        HTTPException: プロジェクトが見つからない場合
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # Tenant isolation check
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="このプロジェクトにアクセスする権限がありません")

    # Get photos for this project
    photos = (
        db.query(Photo)
        .filter(Photo.project_id == project_id)
        .order_by(Photo.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return photos


@router.get("/{project_id}/stats", response_model=ProjectStatsResponse)
async def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    プロジェクト統計情報を取得

    Args:
        project_id: プロジェクトID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ProjectStatsResponse: プロジェクト統計情報

    Raises:
        HTTPException: プロジェクトが見つからない場合
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # Tenant isolation check
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="このプロジェクトにアクセスする権限がありません")

    # Total photo count
    photo_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project_id
    ).scalar() or 0

    # Today's uploads
    today = datetime.utcnow().date()
    today_uploads = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project_id,
        func.date(Photo.created_at) == today
    ).scalar() or 0

    # This week's uploads
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    this_week_uploads = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project_id,
        Photo.created_at >= week_start
    ).scalar() or 0

    # Category distribution
    category_distribution = {}
    category_results = db.query(
        Photo.major_category,
        func.count(Photo.id)
    ).filter(
        Photo.project_id == project_id,
        Photo.major_category.isnot(None)
    ).group_by(Photo.major_category).all()

    for category, count in category_results:
        category_distribution[category] = count

    # Quality issues count
    quality_issues_count = db.query(func.count(Photo.id)).filter(
        Photo.project_id == project_id,
        Photo.quality_score < 70
    ).scalar() or 0

    return ProjectStatsResponse(
        project_id=project_id,
        photo_count=photo_count,
        today_uploads=today_uploads,
        this_week_uploads=this_week_uploads,
        category_distribution=category_distribution,
        quality_issues_count=quality_issues_count,
    )
