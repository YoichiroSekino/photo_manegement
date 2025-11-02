"""
FastAPI メインアプリケーション
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.routers import photos, ocr, search, rekognition, duplicate, quality, title, photo_xml

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Construction Photo Management API",
    description="工事写真自動整理システム バックエンドAPI",
    version=__version__,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録（順序重要: 具体的なパスを先に登録）
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
