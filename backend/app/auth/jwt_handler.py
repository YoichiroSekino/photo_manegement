"""
JWT トークン処理
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
import os

# JWT設定
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class JWTHandler:
    """JWT トークン処理クラス"""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        アクセストークンを作成

        Args:
            data: トークンに含めるデータ
            expires_delta: 有効期限

        Returns:
            JWT トークン
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        リフレッシュトークンを作成

        Args:
            data: トークンに含めるデータ

        Returns:
            リフレッシュトークン
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        トークンをデコード

        Args:
            token: JWT トークン

        Returns:
            デコードされたペイロード、無効な場合はNone
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        パスワードを検証

        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化されたパスワード

        Returns:
            検証結果
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        パスワードをハッシュ化

        Args:
            password: 平文パスワード

        Returns:
            ハッシュ化されたパスワード
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')


def create_tokens(user_id: int, email: str, organization_id: int) -> Dict[str, str]:
    """
    アクセストークンとリフレッシュトークンを作成（マルチテナント対応）

    Args:
        user_id: ユーザーID
        email: メールアドレス
        organization_id: 組織ID

    Returns:
        アクセストークンとリフレッシュトークンの辞書
    """
    access_token = JWTHandler.create_access_token(
        data={"sub": str(user_id), "email": email, "org_id": organization_id}
    )
    refresh_token = JWTHandler.create_refresh_token(
        data={"sub": str(user_id), "email": email, "org_id": organization_id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
