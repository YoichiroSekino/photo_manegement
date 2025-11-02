"""
Application configuration settings
環境変数から設定を読み込み、アプリケーション全体で使用する
"""

import os
from functools import lru_cache


class Settings:
    """アプリケーション設定クラス"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://photo_user:photo_password@localhost:5432/construction_photo_db"
    )

    # AWS S3
    S3_BUCKET: str = os.getenv("S3_BUCKET", "construction-photos")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    # Application
    APP_NAME: str = "Construction Photo Management System"
    APP_VERSION: str = "0.5.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # File upload limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".tiff", ".tif"}

    # AI Services
    REKOGNITION_MAX_LABELS: int = int(os.getenv("REKOGNITION_MAX_LABELS", "10"))
    OCR_CONFIDENCE_THRESHOLD: float = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.8"))

    # Quality thresholds
    MIN_PIXEL_COUNT: int = int(os.getenv("MIN_PIXEL_COUNT", "1000000"))  # 1MP
    MAX_PIXEL_COUNT: int = int(os.getenv("MAX_PIXEL_COUNT", "3000000"))  # 3MP
    MIN_SHARPNESS_SCORE: float = float(os.getenv("MIN_SHARPNESS_SCORE", "0.4"))


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()


# グローバル設定インスタンス
settings = get_settings()
