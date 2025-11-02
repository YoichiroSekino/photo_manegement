"""
JWT マルチテナント対応テスト
"""

import pytest
from app.auth.jwt_handler import JWTHandler, create_tokens


class TestJWTMultitenant:
    """JWTマルチテナント対応のテスト"""

    def test_create_tokens_with_organization_id(self):
        """organization_idを含むトークン作成テスト"""
        user_id = 1
        email = "test@example.com"
        organization_id = 5

        tokens = create_tokens(user_id, email, organization_id)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

        # アクセストークンのデコード
        access_payload = JWTHandler.decode_token(tokens["access_token"])
        assert access_payload is not None
        assert access_payload["sub"] == str(user_id)
        assert access_payload["email"] == email
        assert access_payload["org_id"] == organization_id
        assert access_payload["type"] == "access"

        # リフレッシュトークンのデコード
        refresh_payload = JWTHandler.decode_token(tokens["refresh_token"])
        assert refresh_payload is not None
        assert refresh_payload["sub"] == str(user_id)
        assert refresh_payload["email"] == email
        assert refresh_payload["org_id"] == organization_id
        assert refresh_payload["type"] == "refresh"

    def test_create_access_token_with_organization_id(self):
        """organization_idを含むアクセストークン作成テスト"""
        data = {"sub": "123", "email": "user@company.com", "org_id": 10}

        token = JWTHandler.create_access_token(data)
        payload = JWTHandler.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "user@company.com"
        assert payload["org_id"] == 10
        assert payload["type"] == "access"

    def test_create_refresh_token_with_organization_id(self):
        """organization_idを含むリフレッシュトークン作成テスト"""
        data = {"sub": "456", "email": "another@company.com", "org_id": 20}

        token = JWTHandler.create_refresh_token(data)
        payload = JWTHandler.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "456"
        assert payload["email"] == "another@company.com"
        assert payload["org_id"] == 20
        assert payload["type"] == "refresh"

    def test_different_organizations_have_different_tokens(self):
        """異なる組織は異なるトークンを持つことを確認"""
        user_id = 1
        email = "test@example.com"

        tokens_org1 = create_tokens(user_id, email, 1)
        tokens_org2 = create_tokens(user_id, email, 2)

        # トークン文字列は異なる
        assert tokens_org1["access_token"] != tokens_org2["access_token"]

        # デコードして組織IDを確認
        payload1 = JWTHandler.decode_token(tokens_org1["access_token"])
        payload2 = JWTHandler.decode_token(tokens_org2["access_token"])

        assert payload1["org_id"] == 1
        assert payload2["org_id"] == 2

    def test_token_without_organization_id_backwards_compatibility(self):
        """organization_idなしのトークンも動作すること（後方互換性）"""
        # 古い形式（organization_idなし）
        data = {"sub": "999", "email": "legacy@example.com"}

        token = JWTHandler.create_access_token(data)
        payload = JWTHandler.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "999"
        assert payload["email"] == "legacy@example.com"
        # org_idがなくてもエラーにならない
        assert "org_id" not in payload or payload.get("org_id") is None
