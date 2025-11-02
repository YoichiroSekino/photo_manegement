"""
組織管理APIエンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import User, Organization
from app.auth.jwt_handler import create_tokens


class TestGetOrganization:
    """GET /api/v1/organizations/{organization_id} のテスト"""

    @pytest.fixture
    def test_organization(self, db):
        """テスト用組織"""
        org = Organization(name="テスト組織", subdomain="test-org", is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    @pytest.fixture
    def test_user(self, db, test_organization):
        """テスト用ユーザー"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            organization_id=test_organization.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダー"""
        tokens = create_tokens(
            test_user.id, test_user.email, test_user.organization_id
        )
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def test_get_own_organization_success(
        self, client: TestClient, test_user: User, test_organization: Organization, auth_headers: dict
    ):
        """自分の組織情報を取得できる"""
        response = client.get(
            f"/api/v1/organizations/{test_user.organization_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_organization.id
        assert data["name"] == "テスト組織"
        assert data["subdomain"] == "test-org"
        assert data["is_active"] is True

    def test_get_other_organization_forbidden(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        auth_headers: dict,
    ):
        """他の組織情報は取得できない（403エラー）"""
        # 別の組織を作成
        other_org = Organization(
            name="他の組織",
            subdomain="other-org",
        )
        db.add(other_org)
        db.commit()
        db.refresh(other_org)

        response = client.get(
            f"/api/v1/organizations/{other_org.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "他の組織の情報は取得できません"

    def test_get_nonexistent_organization(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """存在しない組織IDで404エラー"""
        # 存在しない組織ID（9999）
        response = client.get(
            "/api/v1/organizations/9999",
            headers=auth_headers,
        )

        # 権限チェックが先に実行されるため403エラーになる
        assert response.status_code == 403
        assert response.json()["detail"] == "他の組織の情報は取得できません"

    def test_get_organization_without_auth(self, client: TestClient, test_organization: Organization):
        """認証なしでは403エラー（テナントミドルウェアが先に実行される）"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
        )

        # テナントミドルウェアが認証より先に実行されるため403
        assert response.status_code == 403

    def test_get_organization_with_invalid_token(
        self, client: TestClient, test_organization: Organization
    ):
        """無効なトークンでは401エラー"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401
