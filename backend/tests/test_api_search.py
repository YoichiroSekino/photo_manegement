"""
検索APIエンドポイントのテスト（マルチテナント対応）
"""

import pytest
from datetime import datetime
from app.database.models import Organization, User
from app.auth.jwt_handler import create_tokens


class TestSearchAPI:
    """検索API テスト"""

    @pytest.fixture
    def test_org(self, db):
        """テスト用組織"""
        org = Organization(name="Test Company", subdomain="testcompany", is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    @pytest.fixture
    def test_user(self, db, test_org):
        """テスト用ユーザー"""
        user = User(
            email="test@testcompany.com",
            hashed_password="hashed",
            organization_id=test_org.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダー"""
        tokens = create_tokens(test_user.id, test_user.email, test_user.organization_id)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @pytest.fixture
    def sample_photos(self, client, auth_headers):
        """テスト用サンプル写真データ"""
        photos_data = [
            {
                "file_name": "土工_掘削_001.jpg",
                "file_size": 1024000,
                "mime_type": "image/jpeg",
                "s3_key": "photos/001.jpg",
                "title": "掘削作業",
                "description": "基礎掘削の施工状況",
                "shooting_date": "2024-03-15T10:00:00",
                "work_type": "土工",
                "work_kind": "掘削工",
                "major_category": "工事",
                "photo_type": "施工状況写真",
            },
            {
                "file_name": "基礎工_配筋_002.jpg",
                "file_size": 2048000,
                "mime_type": "image/jpeg",
                "s3_key": "photos/002.jpg",
                "title": "配筋検査",
                "description": "基礎配筋の検査写真",
                "shooting_date": "2024-03-20T14:30:00",
                "work_type": "基礎工",
                "work_kind": "配筋工",
                "major_category": "工事",
                "photo_type": "品質管理写真",
            },
            {
                "file_name": "土工_埋戻_003.jpg",
                "file_size": 1536000,
                "mime_type": "image/jpeg",
                "s3_key": "photos/003.jpg",
                "title": "埋戻し作業",
                "description": "埋戻しの施工状況",
                "shooting_date": "2024-04-05T09:15:00",
                "work_type": "土工",
                "work_kind": "埋戻工",
                "major_category": "工事",
                "photo_type": "施工状況写真",
            },
            {
                "file_name": "基礎工_型枠_004.jpg",
                "file_size": 1800000,
                "mime_type": "image/jpeg",
                "s3_key": "photos/004.jpg",
                "title": "型枠設置",
                "description": "基礎型枠の設置状況",
                "shooting_date": "2024-04-10T11:00:00",
                "work_type": "基礎工",
                "work_kind": "型枠工",
                "major_category": "安全",
                "photo_type": "安全管理写真",
            },
        ]

        photo_ids = []
        for photo_data in photos_data:
            response = client.post(
                "/api/v1/photos", json=photo_data, headers=auth_headers
            )
            assert response.status_code == 201
            photo_ids.append(response.json()["id"])

        return photo_ids

    def test_search_by_keyword(self, client, auth_headers, sample_photos):
        """キーワード検索のテスト"""
        # "掘削"で検索
        response = client.get(
            "/api/v1/photos/search?keyword=掘削", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

        # 結果に"掘削"が含まれることを確認
        for item in data["items"]:
            assert (
                "掘削" in item.get("title", "")
                or "掘削" in item.get("description", "")
                or "掘削" in item.get("file_name", "")
                or "掘削" in item.get("work_kind", "")
            )

    def test_search_by_work_type(self, client, auth_headers, sample_photos):
        """工種フィルタのテスト"""
        # "土工"で検索
        response = client.get(
            "/api/v1/photos/search?work_type=土工", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # 土工の写真は2件
        assert len(data["items"]) == 2

        for item in data["items"]:
            assert item["work_type"] == "土工"

    def test_search_by_date_range(self, client, auth_headers, sample_photos):
        """日付範囲検索のテスト"""
        # 2024-03-01 から 2024-03-31 の範囲で検索
        response = client.get(
            "/api/v1/photos/search?date_from=2024-03-01&date_to=2024-03-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # 3月の写真は2件

        for item in data["items"]:
            shooting_date = datetime.fromisoformat(
                item["shooting_date"].replace("Z", "+00:00")
            )
            assert (
                datetime(2024, 3, 1)
                <= shooting_date
                <= datetime(2024, 3, 31, 23, 59, 59)
            )

    def test_search_with_multiple_conditions(self, client, auth_headers, sample_photos):
        """複合検索条件のテスト"""
        # キーワード"基礎" + 工種"基礎工" + 日付範囲
        response = client.get(
            "/api/v1/photos/search?keyword=基礎&work_type=基礎工&date_from=2024-03-01&date_to=2024-03-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1  # 条件を満たすのは1件

        item = data["items"][0]
        assert item["work_type"] == "基礎工"
        assert "基礎" in item["title"] or "基礎" in item["description"]

    def test_search_with_pagination(self, client, auth_headers, sample_photos):
        """ページネーション付き検索のテスト"""
        # ページサイズ2で検索
        response = client.get(
            "/api/v1/photos/search?page=1&page_size=2", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total"] == 4
        assert data["total_pages"] == 2

        # 2ページ目を取得
        response = client.get(
            "/api/v1/photos/search?page=2&page_size=2", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["items"]) == 2

    def test_search_no_results(self, client, auth_headers, sample_photos):
        """検索結果なしのテスト"""
        response = client.get(
            "/api/v1/photos/search?keyword=存在しないキーワード", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_search_all_photos(self, client, auth_headers, sample_photos):
        """全件検索のテスト（条件なし）"""
        response = client.get("/api/v1/photos/search", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert len(data["items"]) == 4

    def test_search_by_work_kind(self, client, auth_headers, sample_photos):
        """種別検索のテスト"""
        response = client.get(
            "/api/v1/photos/search?work_kind=配筋工", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["work_kind"] == "配筋工"

    def test_search_invalid_date_range(self, client, auth_headers, sample_photos):
        """無効な日付範囲のテスト"""
        # date_fromがdate_toより後
        response = client.get(
            "/api/v1/photos/search?date_from=2024-12-31&date_to=2024-01-01",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0  # 該当なし

    def test_search_by_major_category(self, client, auth_headers, sample_photos):
        """写真大分類フィルターのテスト"""
        # "工事"で検索
        response = client.get(
            "/api/v1/photos/search?major_category=工事", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3  # 工事の写真は3件
        assert len(data["items"]) == 3

        for item in data["items"]:
            assert item["major_category"] == "工事"

    def test_search_by_photo_type(self, client, auth_headers, sample_photos):
        """写真区分フィルターのテスト"""
        # "施工状況写真"で検索
        response = client.get(
            "/api/v1/photos/search?photo_type=施工状況写真", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # 施工状況写真は2件
        assert len(data["items"]) == 2

        for item in data["items"]:
            assert item["photo_type"] == "施工状況写真"

    def test_unauthenticated_search(self, client):
        """認証なし検索は拒否される"""
        response = client.get("/api/v1/photos/search")
        assert response.status_code == 403  # HTTPBearer returns 403
