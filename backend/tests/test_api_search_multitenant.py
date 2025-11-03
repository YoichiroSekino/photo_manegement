"""
検索APIマルチテナント対応テスト
"""

import pytest
from datetime import datetime
from app.database.models import Organization, User, Photo, Project
from app.auth.jwt_handler import create_tokens


class TestSearchAPIMultitenant:
    """検索APIマルチテナント対応テスト"""

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
    def test_projects(self, db, test_organizations):
        """テスト用プロジェクト"""
        org1, org2 = test_organizations

        project1 = Project(
            name="Project A1",
            description="Organization A Project 1",
            organization_id=org1.id,
        )
        project2 = Project(
            name="Project A2",
            description="Organization A Project 2",
            organization_id=org1.id,
        )
        project3 = Project(
            name="Project B1",
            description="Organization B Project 1",
            organization_id=org2.id,
        )
        db.add_all([project1, project2, project3])
        db.commit()
        db.refresh(project1)
        db.refresh(project2)
        db.refresh(project3)
        return project1, project2, project3

    @pytest.fixture
    def test_photos(self, db, test_organizations, test_projects):
        """テスト用写真"""
        org1, org2 = test_organizations
        project1, project2, project3 = test_projects

        # org1の写真
        photo1 = Photo(
            file_name="bridge_construction.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/photo1.jpg",
            organization_id=org1.id,
            project_id=project1.id,
            title="橋梁工事",
            description="橋の建設現場",
            work_type="橋梁工事",
            work_kind="基礎工事",
            major_category="施工状況写真",
            shooting_date=datetime(2024, 1, 15),
        )
        photo2 = Photo(
            file_name="road_construction.jpg",
            file_size=2048,
            mime_type="image/jpeg",
            s3_key="photos/photo2.jpg",
            organization_id=org1.id,
            project_id=project2.id,
            title="道路工事",
            description="道路舗装工事",
            work_type="道路工事",
            work_kind="舗装工事",
            major_category="施工状況写真",
            shooting_date=datetime(2024, 2, 20),
        )

        # org2の写真
        photo3 = Photo(
            file_name="tunnel_construction.jpg",
            file_size=3072,
            mime_type="image/jpeg",
            s3_key="photos/photo3.jpg",
            organization_id=org2.id,
            project_id=project3.id,
            title="トンネル工事",
            description="トンネル掘削現場",
            work_type="トンネル工事",
            work_kind="掘削工事",
            major_category="施工状況写真",
            shooting_date=datetime(2024, 3, 10),
        )

        db.add_all([photo1, photo2, photo3])
        db.commit()
        return photo1, photo2, photo3

    def test_search_all_photos_filtered_by_organization(
        self, client, db, test_users, test_projects, test_photos
    ):
        """検索結果が組織でフィルタリングされることを確認"""
        user1, user2 = test_users
        photo1, photo2, photo3 = test_photos

        # user1（org1）で検索
        tokens1 = create_tokens(user1.id, user1.email, user1.organization_id)
        response1 = client.get(
            "/api/v1/photos/search",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 2  # org1の写真は2枚
        photo_ids1 = [item["id"] for item in data1["items"]]
        assert photo1.id in photo_ids1
        assert photo2.id in photo_ids1
        assert photo3.id not in photo_ids1  # org2の写真は含まれない

        # user2（org2）で検索
        tokens2 = create_tokens(user2.id, user2.email, user2.organization_id)
        response2 = client.get(
            "/api/v1/photos/search",
            headers={"Authorization": f"Bearer {tokens2['access_token']}"},
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1  # org2の写真は1枚
        photo_ids2 = [item["id"] for item in data2["items"]]
        assert photo3.id in photo_ids2
        assert photo1.id not in photo_ids2  # org1の写真は含まれない
        assert photo2.id not in photo_ids2

    def test_search_with_keyword_filtered_by_organization(
        self, client, db, test_users, test_projects, test_photos
    ):
        """キーワード検索が組織でフィルタリングされることを確認"""
        user1, user2 = test_users
        photo1, photo2, photo3 = test_photos

        # user1が「橋梁」で検索 -> org1の写真のみ
        tokens1 = create_tokens(user1.id, user1.email, user1.organization_id)
        response1 = client.get(
            "/api/v1/photos/search?keyword=橋梁",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 1
        assert data1["items"][0]["id"] == photo1.id

        # user2が「橋梁」で検索 -> org2に該当する写真なし
        tokens2 = create_tokens(user2.id, user2.email, user2.organization_id)
        response2 = client.get(
            "/api/v1/photos/search?keyword=橋梁",
            headers={"Authorization": f"Bearer {tokens2['access_token']}"},
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 0

    def test_search_with_filters_filtered_by_organization(
        self, client, db, test_users, test_projects, test_photos
    ):
        """フィルタ検索が組織でフィルタリングされることを確認"""
        user1, _ = test_users
        photo1, photo2, _ = test_photos

        # user1が工種で検索
        tokens1 = create_tokens(user1.id, user1.email, user1.organization_id)
        response = client.get(
            "/api/v1/photos/search?work_type=橋梁工事",
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == photo1.id

    def test_search_unauthenticated_access_denied(
        self, client, db, test_projects, test_photos
    ):
        """認証なし検索は拒否されることを確認"""
        # 認証なしで検索 -> 403
        response = client.get("/api/v1/photos/search")
        assert response.status_code == 403
