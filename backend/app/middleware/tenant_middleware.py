"""
テナント識別ミドルウェア
"""

from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Organization


class TenantIdentificationMiddleware(BaseHTTPMiddleware):
    """
    テナント識別ミドルウェア

    リクエストからテナント（組織）を識別し、request.state.organizationに設定する

    識別方法:
    1. X-Organization-Subdomain ヘッダー（優先）
    2. サブドメイン (例: companya.example.com -> companya)
    3. デフォルト組織 (開発環境用)
    """

    async def dispatch(self, request: Request, call_next):
        """
        リクエストごとに実行されるメソッド

        Args:
            request: HTTPリクエスト
            call_next: 次のミドルウェア/エンドポイント

        Returns:
            HTTPレスポンス
        """
        # テナント識別をスキップするパス
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        if any(request.url.path.startswith(path) for path in skip_paths):
            # 認証不要なパスはスキップ
            return await call_next(request)

        # 組織識別
        organization = None
        db: Session = SessionLocal()

        try:
            # 1. ヘッダーから識別（APIクライアント用）
            subdomain_header = request.headers.get("X-Organization-Subdomain")

            if subdomain_header:
                organization = (
                    db.query(Organization)
                    .filter(
                        Organization.subdomain == subdomain_header,
                        Organization.is_active == True,
                    )
                    .first()
                )

                if not organization:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"組織が見つかりません: {subdomain_header}",
                    )

            # 2. サブドメインから識別（Webアプリ用）
            elif request.url.hostname:
                hostname_parts = request.url.hostname.split(".")

                # サブドメインが存在する場合（例: companya.example.com）
                if len(hostname_parts) >= 3:
                    subdomain = hostname_parts[0]

                    # localhost やIPアドレスでない場合のみ
                    if subdomain not in ["localhost", "127", "192", "10"]:
                        organization = (
                            db.query(Organization)
                            .filter(
                                Organization.subdomain == subdomain,
                                Organization.is_active == True,
                            )
                            .first()
                        )

            # 3. デフォルト組織（開発環境用）
            if not organization:
                # ヘッダーもサブドメインも指定されていない場合はデフォルト組織を使用
                organization = (
                    db.query(Organization)
                    .filter(
                        Organization.subdomain == "default",
                        Organization.is_active == True,
                    )
                    .first()
                )

                # デフォルト組織も見つからない場合はエラー
                if not organization:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="デフォルト組織が設定されていません",
                    )

            # request.stateに組織情報を設定
            request.state.organization = organization
            request.state.organization_id = organization.id
            request.state.organization_subdomain = organization.subdomain

        finally:
            db.close()

        # 次のミドルウェア/エンドポイントを実行
        response = await call_next(request)

        # レスポンスヘッダーに組織情報を追加（デバッグ用）
        if organization:
            response.headers["X-Organization-ID"] = str(organization.id)
            response.headers["X-Organization-Subdomain"] = organization.subdomain

        return response


def get_current_organization(request: Request) -> Organization:
    """
    現在のリクエストの組織を取得

    Args:
        request: HTTPリクエスト

    Returns:
        Organization: 組織オブジェクト

    Raises:
        HTTPException: 組織が設定されていない場合
    """
    if not hasattr(request.state, "organization"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="組織情報が設定されていません",
        )

    return request.state.organization


def get_current_organization_id(request: Request) -> int:
    """
    現在のリクエストの組織IDを取得

    Args:
        request: HTTPリクエスト

    Returns:
        int: 組織ID

    Raises:
        HTTPException: 組織IDが設定されていない場合
    """
    if not hasattr(request.state, "organization_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="組織IDが設定されていません",
        )

    return request.state.organization_id
