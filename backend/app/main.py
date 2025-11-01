"""
FastAPI メインアプリケーション
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.routers import photos, ocr

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

# ルーター登録
app.include_router(photos.router)
app.include_router(ocr.router)


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
