"""
認証APIルーター
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.database import get_db
from app.database.models import User
from app.auth.jwt_handler import JWTHandler, create_tokens
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)


class UserRegister(BaseModel):
    """ユーザー登録リクエスト"""

    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    """ログインリクエスト"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """トークンレスポンス"""

    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    """ユーザーレスポンス"""

    id: int
    email: str
    full_name: str | None
    is_active: bool

    class Config:
        from_attributes = True


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    新規ユーザー登録

    Args:
        user_data: ユーザー登録データ
        db: データベースセッション

    Returns:
        作成されたユーザー

    Raises:
        HTTPException: メールアドレスが既に登録されている場合
    """
    # メールアドレスの重複チェック
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # パスワードをハッシュ化
    hashed_password = JWTHandler.get_password_hash(user_data.password)

    # 新規ユーザー作成
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, credentials: UserLogin, db: Session = Depends(get_db)
):
    """
    ユーザーログイン

    Args:
        credentials: ログイン認証情報
        db: データベースセッション

    Returns:
        アクセストークンとリフレッシュトークン

    Raises:
        HTTPException: 認証に失敗した場合
    """
    # ユーザーを検索
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    # パスワードを検証
    if not JWTHandler.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    # ユーザーがアクティブか確認
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このアカウントは無効化されています",
        )

    # トークンを作成
    tokens = create_tokens(user.id, user.email)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    現在のユーザー情報を取得

    Args:
        current_user: 現在の認証済みユーザー

    Returns:
        ユーザー情報
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    リフレッシュトークンを使用して新しいアクセストークンを取得

    Args:
        refresh_token: リフレッシュトークン
        db: データベースセッション

    Returns:
        新しいトークンペア

    Raises:
        HTTPException: トークンが無効な場合
    """
    # トークンをデコード
    payload = JWTHandler.decode_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです",
        )

    # トークンタイプを確認
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンタイプです",
        )

    # ユーザーIDを取得
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンにユーザー情報が含まれていません",
        )

    # ユーザーを検索
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つからないか、無効化されています",
        )

    # 新しいトークンを作成
    tokens = create_tokens(user.id, user.email)
    return tokens
