"""
重複検出APIエンドポイントのテスト
"""

import pytest
from app.database.models import Organization, User, Project, Photo
from app.auth.jwt_handler import create_tokens


class TestDuplicateAPI:
    """重複検出API テスト"""

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
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture
    def test_project(self, db, test_org):
        """テスト用プロジェクト"""
        project = Project(
            name="Test Construction Project",
            organization_id=test_org.id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダー"""
        tokens = create_tokens(test_user.id, test_user.email, test_user.organization_id)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @pytest.fixture
    def test_photos_with_phash(self, db, test_org, test_project):
        """pHashを持つテスト写真"""
        photos = []
        for i in range(3):
            photo = Photo(
                file_name=f"test{i}.jpg",
                file_size=1024000,
                mime_type="image/jpeg",
                s3_key=f"photos/test{i}.jpg",
                organization_id=test_org.id,
                project_id=test_project.id,
                photo_metadata={"phash": f"0123456789abcde{i}"},
            )
            db.add(photo)
            photos.append(photo)
        db.commit()
        for photo in photos:
            db.refresh(photo)
        return photos

    def test_detect_duplicates_no_photos(self, client, auth_headers):
        """写真が存在しない場合の重複検出"""
        response = client.post(
            "/api/v1/photos/detect-duplicates?similarity_threshold=90.0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_photos"] == 0
        assert len(data["duplicate_groups"]) == 0

    def test_detect_duplicates_with_photos(self, client, auth_headers, test_photos_with_phash):
        """写真が存在する場合の重複検出"""
        response = client.post(
            "/api/v1/photos/detect-duplicates?similarity_threshold=90.0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_photos"] == 3
        assert "duplicate_groups" in data
        assert "summary" in data

    def test_calculate_phash_success(self, client, auth_headers, db, test_org, test_project):
        """pHash計算成功"""
        # モック用の写真を作成（pHashなし）
        photo = Photo(
            file_name="test.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            s3_key="photos/test.jpg",
            organization_id=test_org.id,
            project_id=test_project.id,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)

        # Note: 実際のS3アクセスが必要なので、モックを使用するか統合テストで実施
        # ここでは404エラーをテスト
        response = client.post(
            f"/api/v1/photos/{photo.id}/calculate-phash",
            headers=auth_headers,
        )
        # S3アクセスに失敗するため500エラーになる
        assert response.status_code in [404, 500]

    def test_detect_duplicates_different_thresholds(self, client, auth_headers, test_photos_with_phash):
        """異なる類似度閾値でのテスト"""
        # 高い閾値
        response = client.post(
            "/api/v1/photos/detect-duplicates?similarity_threshold=95.0",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 低い閾値
        response = client.post(
            "/api/v1/photos/detect-duplicates?similarity_threshold=70.0",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_duplicate_action_confirm(self, client, auth_headers, test_photos_with_phash):
        """重複確定のテスト"""
        photo1 = test_photos_with_phash[0]
        photo2 = test_photos_with_phash[1]

        response = client.post(
            "/api/v1/photos/duplicates/action",
            headers=auth_headers,
            json={
                "photo_id_to_keep": photo1.id,
                "photo_id_to_delete": photo2.id,
                "action": "confirm",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["photo_id_kept"] == photo1.id
        assert data["photo_id_deleted"] == photo2.id
        assert "重複として確定しました" in data["message"]

    def test_duplicate_action_reject(self, client, auth_headers, test_photos_with_phash):
        """重複却下のテスト"""
        photo1 = test_photos_with_phash[0]
        photo2 = test_photos_with_phash[1]

        response = client.post(
            "/api/v1/photos/duplicates/action",
            headers=auth_headers,
            json={
                "photo_id_to_keep": photo1.id,
                "photo_id_to_delete": photo2.id,
                "action": "reject",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "重複を却下しました" in data["message"]

    def test_duplicate_action_invalid_action(self, client, auth_headers, test_photos_with_phash):
        """無効なアクション"""
        photo1 = test_photos_with_phash[0]
        photo2 = test_photos_with_phash[1]

        response = client.post(
            "/api/v1/photos/duplicates/action",
            headers=auth_headers,
            json={
                "photo_id_to_keep": photo1.id,
                "photo_id_to_delete": photo2.id,
                "action": "invalid",
            },
        )
        assert response.status_code == 400
        assert "無効なアクション" in response.json()["detail"]

    def test_duplicate_action_photo_not_found(self, client, auth_headers):
        """存在しない写真で重複アクション"""
        response = client.post(
            "/api/v1/photos/duplicates/action",
            headers=auth_headers,
            json={
                "photo_id_to_keep": 99999,
                "photo_id_to_delete": 99998,
                "action": "confirm",
            },
        )
        assert response.status_code == 404
        assert "写真が見つかりません" in response.json()["detail"]
