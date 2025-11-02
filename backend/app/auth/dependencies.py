"""
認証用の依存関数
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.auth.jwt_handler import JWTHandler

# HTTPBearer認証スキーム
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    現在の認証済みユーザーを取得

    Args:
        credentials: HTTPベアラー認証情報
        db: データベースセッション

    Returns:
        ユーザーオブジェクト

    Raises:
        HTTPException: 認証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # トークンをデコード
    token = credentials.credentials
    payload = JWTHandler.decode_token(token)

    if payload is None:
        raise credentials_exception

    # トークンタイプを確認
    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception

    # ユーザーIDを取得
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # データベースからユーザーを取得
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のアクティブユーザーを取得

    Args:
        current_user: 現在のユーザー

    Returns:
        アクティブユーザー

    Raises:
        HTTPException: ユーザーが非アクティブの場合
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="非アクティブユーザーです"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    現在のユーザーを取得（オプション）

    認証が必須でないエンドポイント用。
    トークンが提供されていればユーザーを返し、なければNoneを返す。

    Args:
        credentials: HTTPベアラー認証情報（オプション）
        db: データベースセッション

    Returns:
        ユーザーオブジェクト、または None
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = JWTHandler.decode_token(token)

        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except Exception:
        return None
