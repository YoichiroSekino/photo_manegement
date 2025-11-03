"""
FastAPI メインアプリケーション
"""

from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app import __version__
from app.routers import (
    photos,
    ocr,
    search,
    rekognition,
    duplicate,
    quality,
    title,
    photo_xml,
    export,
    photo_album,
    auth,
    organizations,
    projects,
    dashboard,
)
from app.middleware import TenantIdentificationMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Rate limiter初期化
limiter = Limiter(key_func=get_remote_address)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Construction Photo Management API",
    description="工事写真自動整理システム バックエンドAPI",
    version=__version__,
)

# Rate limiterをアプリケーションに追加
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# テナント識別ミドルウェア（CORSより先に実行）
app.add_middleware(TenantIdentificationMiddleware)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録（順序重要: 具体的なパスを先に登録）
app.include_router(auth.router)  # /api/v1/auth
app.include_router(organizations.router)  # /api/v1/organizations
app.include_router(projects.router)  # /api/v1/projects
app.include_router(dashboard.router)  # /api/v1/dashboard
app.include_router(photo_album.router)  # /api/v1/photo-album/generate-pdf
app.include_router(export.router)  # /api/v1/export/package
app.include_router(photo_xml.router)  # /api/v1/photo-xml/generate
app.include_router(search.router)  # /api/v1/photos/search
app.include_router(duplicate.router)  # /api/v1/photos/detect-duplicates
app.include_router(quality.router)  # /api/v1/photos/{photo_id}/assess-quality
app.include_router(title.router)  # /api/v1/photos/{photo_id}/generate-title
app.include_router(rekognition.router)  # /api/v1/photos/{photo_id}/classify
app.include_router(ocr.router)  # /api/v1/photos/{photo_id}/process-ocr
app.include_router(photos.router)  # /api/v1/photos/{photo_id}


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "工事写真自動整理システム API"}


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "version": __version__}


@app.get("/api/v1/info")
async def api_info():
    """API情報エンドポイント"""
    return {
        "name": "Construction Photo Management API",
        "version": __version__,
        "description": "工事写真自動整理システム バックエンドAPI",
    }


# 開発環境用：静的ファイル配信（全ルーター登録後にマウント）
if os.getenv("USE_MOCK_S3", "true").lower() == "true":
    # アップロード用ディレクトリ作成
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # 静的ファイルをマウント（最後にマウントすることでAPIルートとの競合を防ぐ）
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")
