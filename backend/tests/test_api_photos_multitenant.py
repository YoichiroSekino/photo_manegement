"""
写真APIマルチテナント対応テスト
"""

import pytest
from app.database.models import Organization, User, Photo
from app.auth.jwt_handler import create_tokens


class TestPhotosAPIMultitenant:
    """写真APIマルチテナント対応テスト"""

    @pytest.fixture
    def test_organizations(self, db):
        """テスト用組織"""
        org1 = Organization(name="Company A", subdomain="companya", is_active=True)
        org2 = Organization(name="Company B", subdomain="companyb", is_active=True)
        db.add(org1)
        db.add(org2)
        db.commit()
        db.refresh(org1)
        db.refresh(org2)
        return org1, org2

    @pytest.fixture
    def test_users(self, db, test_organizations):
        """テスト用ユーザー"""
        org1, org2 = test_organizations

        user1 = User(
            email="user1@companya.com",
            hashed_password="hashed1",
            organization_id=org1.id,
            is_active=True,
        )
        user2 = User(
            email="user2@companyb.com",
            hashed_password="hashed2",
            organization_id=org2.id,
            is_active=True,
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        return user1, user2

    @pytest.fixture
    def test_photos(self, db, test_organizations):
        """テスト用写真"""
        org1, org2 = test_organizations

        # org1の写真
        photo1 = Photo(
            file_name="photo1.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/photo1.jpg",
            organization_id=org1.id,
        )
        photo2 = Photo(
            file_name="photo2.jpg",
            file_size=2048,
            mime_type="image/jpeg",
            s3_key="photos/photo2.jpg",
            organization_id=org1.id,
        )

        # org2の写真
        photo3 = Photo(
            file_name="photo3.jpg",
            file_size=3072,
            mime_type="image/jpeg",
            s3_key="photos/photo3.jpg",
            organization_id=org2.id,
        )

        db.add_all([photo1, photo2, photo3])
        db.commit()
        return photo1, photo2, photo3

    def test_create_photo_auto_assigns_organization_id(self, client, db, test_users):
        """写真作成時にorganization_idが自動的に設定されることを確認"""
        user1, _ = test_users

        # JWTトークン作成
        tokens = create_tokens(user1.id, user1.email, user1.organization_id)
        access_token = tokens["access_token"]

        # 写真作成リクエスト
        photo_data = {
            "file_name": "new_photo.jpg",
            "file_size": 5000,
            "mime_type": "image/jpeg",
            "s3_key": "photos/new_photo.jpg",
        }

        response = client.post(
            "/api/v1/photos",
            json=photo_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["organization_id"] == user1.organization_id

    def test_get_photos_filtered_by_organization(
        self, client, db, test_users, test_photos
    ):
        """写真一覧が組織でフィルタリングされることを確認"""
        user1, user2 = test_users
        photo1, photo2, photo3 = test_photos

        # user1（org1）でアクセス
        tokens1 = create_tokens(user1.id, user1.email, user1.organization_id)
        response1 = client.get(
            "/api/v1/photos",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 2  # org1の写真は2枚
        photo_ids1 = [item["id"] for item in data1["items"]]
        assert photo1.id in photo_ids1
        assert photo2.id in photo_ids1
        assert photo3.id not in photo_ids1  # org2の写真は含まれない

        # user2（org2）でアクセス
        tokens2 = create_tokens(user2.id, user2.email, user2.organization_id)
        response2 = client.get(
            "/api/v1/photos",
            headers={"Authorization": f"Bearer {tokens2['access_token']}"},
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1  # org2の写真は1枚
        photo_ids2 = [item["id"] for item in data2["items"]]
        assert photo3.id in photo_ids2
        assert photo1.id not in photo_ids2  # org1の写真は含まれない
        assert photo2.id not in photo_ids2

    def test_get_photo_by_id_requires_same_organization(
        self, client, db, test_users, test_photos
    ):
        """写真詳細取得は同じ組織のみアクセス可能であることを確認"""
        user1, user2 = test_users
        photo1, _, photo3 = test_photos

        # user1が自組織の写真にアクセス -> OK
        tokens1 = create_tokens(user1.id, user1.email, user1.organization_id)
        response1 = client.get(
            f"/api/v1/photos/{photo1.id}",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )
        assert response1.status_code == 200
        assert response1.json()["id"] == photo1.id

        # user1が他組織の写真にアクセス -> 404
        response2 = client.get(
            f"/api/v1/photos/{photo3.id}",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )
        assert response2.status_code == 404

    def test_unauthenticated_access_denied(self, client, db, test_photos):
        """認証なしアクセスは拒否されることを確認"""
        # 認証なしで写真一覧にアクセス -> 403 (FastAPI HTTPBearer behavior)
        response = client.get("/api/v1/photos")
        assert response.status_code == 403
