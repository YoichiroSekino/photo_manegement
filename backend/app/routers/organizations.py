"""
組織管理APIルーター
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import Organization, User
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


class OrganizationResponse(BaseModel):
    """組織レスポンス"""

    id: int
    name: str
    subdomain: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    組織情報を取得する

    Args:
        organization_id: 組織ID
        db: データベースセッション
        current_user: 現在の認証済みユーザー

    Returns:
        組織情報

    Raises:
        HTTPException: 組織が見つからない、または権限がない場合
    """
    # 自分の組織のみ取得可能
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="他の組織の情報は取得できません"
        )

    organization = (
        db.query(Organization).filter(Organization.id == organization_id).first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="組織が見つかりません"
        )

    return organization
