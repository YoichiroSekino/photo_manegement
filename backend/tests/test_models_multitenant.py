"""
既存モデルのマルチテナント対応テスト
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Organization, User, Photo, Project, PhotoDuplicate


class TestMultitenantModels:
    """既存モデルのマルチテナント対応テスト"""

    @pytest.fixture
    def db(self):
        """テスト用のSQLiteデータベース"""
        # SQLiteでFOREIGN KEYサポートを有効化
        from sqlalchemy import event

        engine = create_engine("sqlite:///:memory:")

        # FOREIGN KEYサポートを有効化（CASCADE動作のため）
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        TestingSessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        yield db
        db.close()

    @pytest.fixture
    def sample_organizations(self, db):
        """テスト用組織データ"""
        org1 = Organization(name="Company A", subdomain="companya", is_active=True)
        org2 = Organization(name="Company B", subdomain="companyb", is_active=True)
        db.add(org1)
        db.add(org2)
        db.commit()
        db.refresh(org1)
        db.refresh(org2)
        return org1, org2

    def test_user_has_organization_id(self, db, sample_organizations):
        """Userモデルにorganization_idが存在することを確認"""
        org1, _ = sample_organizations

        user = User(
            email="test@example.com",
            hashed_password="hashed",
            full_name="Test User",
            organization_id=org1.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.organization_id == org1.id
        assert user.organization.name == "Company A"

    def test_user_organization_id_required(self, db, sample_organizations):
        """Userのorganization_idが必須であることを確認"""
        user = User(
            email="noorg@example.com", hashed_password="hashed"
        )  # organization_idなし

        db.add(user)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_photo_has_organization_id(self, db, sample_organizations):
        """Photoモデルにorganization_idが存在することを確認"""
        org1, _ = sample_organizations

        photo = Photo(
            file_name="test.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            s3_key="photos/test.jpg",
            organization_id=org1.id,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)

        assert photo.organization_id == org1.id
        assert photo.organization.name == "Company A"

    def test_photo_organization_id_required(self, db, sample_organizations):
        """Photoのorganization_idが必須であることを確認"""
        photo = Photo(
            file_name="test.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            s3_key="photos/noorg.jpg",
        )  # organization_idなし

        db.add(photo)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_project_has_organization_id(self, db, sample_organizations):
        """Projectモデルにorganization_idが存在することを確認"""
        org1, _ = sample_organizations

        project = Project(
            name="Test Project", description="Test Description", organization_id=org1.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        assert project.organization_id == org1.id
        assert project.organization.name == "Company A"

    def test_project_organization_id_required(self, db, sample_organizations):
        """Projectのorganization_idが必須であることを確認"""
        project = Project(name="No Org Project")  # organization_idなし

        db.add(project)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_photo_duplicate_has_organization_id(self, db, sample_organizations):
        """PhotoDuplicateモデルにorganization_idが存在することを確認"""
        org1, _ = sample_organizations

        # テスト用写真作成
        photo1 = Photo(
            file_name="p1.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/p1.jpg",
            organization_id=org1.id,
        )
        photo2 = Photo(
            file_name="p2.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/p2.jpg",
            organization_id=org1.id,
        )
        db.add(photo1)
        db.add(photo2)
        db.commit()

        duplicate = PhotoDuplicate(
            photo1_id=photo1.id,
            photo2_id=photo2.id,
            similarity_score=0.95,
            organization_id=org1.id,
        )
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)

        assert duplicate.organization_id == org1.id
        assert duplicate.organization.name == "Company A"

    def test_tenant_isolation_users(self, db, sample_organizations):
        """テナント間でユーザーが分離されることを確認"""
        org1, org2 = sample_organizations

        user1 = User(
            email="user1@companya.com", hashed_password="hash1", organization_id=org1.id
        )
        user2 = User(
            email="user2@companyb.com", hashed_password="hash2", organization_id=org2.id
        )
        db.add(user1)
        db.add(user2)
        db.commit()

        # org1のユーザーのみ取得
        org1_users = db.query(User).filter(User.organization_id == org1.id).all()
        assert len(org1_users) == 1
        assert org1_users[0].email == "user1@companya.com"

        # org2のユーザーのみ取得
        org2_users = db.query(User).filter(User.organization_id == org2.id).all()
        assert len(org2_users) == 1
        assert org2_users[0].email == "user2@companyb.com"

    def test_tenant_isolation_photos(self, db, sample_organizations):
        """テナント間で写真が分離されることを確認"""
        org1, org2 = sample_organizations

        photo1 = Photo(
            file_name="org1.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/org1.jpg",
            organization_id=org1.id,
        )
        photo2 = Photo(
            file_name="org2.jpg",
            file_size=2048,
            mime_type="image/jpeg",
            s3_key="photos/org2.jpg",
            organization_id=org2.id,
        )
        db.add(photo1)
        db.add(photo2)
        db.commit()

        # org1の写真のみ取得
        org1_photos = db.query(Photo).filter(Photo.organization_id == org1.id).all()
        assert len(org1_photos) == 1
        assert org1_photos[0].file_name == "org1.jpg"

        # org2の写真のみ取得
        org2_photos = db.query(Photo).filter(Photo.organization_id == org2.id).all()
        assert len(org2_photos) == 1
        assert org2_photos[0].file_name == "org2.jpg"

    def test_cascade_delete_organization(self, db, sample_organizations):
        """組織削除時の関連データのカスケード動作を確認"""
        org1, _ = sample_organizations

        # テストデータ作成
        user = User(
            email="test@example.com", hashed_password="hash", organization_id=org1.id
        )
        photo = Photo(
            file_name="test.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key="photos/test.jpg",
            organization_id=org1.id,
        )
        db.add(user)
        db.add(photo)
        db.commit()

        # 組織削除前のカウント
        user_count_before = db.query(User).count()
        photo_count_before = db.query(Photo).count()
        assert user_count_before == 1
        assert photo_count_before == 1

        # 組織削除
        db.delete(org1)
        db.commit()

        # カスケード削除されることを確認（または制約エラー）
        # 実装方針によって動作が異なる可能性があるため、
        # ここでは組織削除後のユーザー・写真の存在を確認
        remaining_users = db.query(User).filter(User.organization_id == org1.id).all()
        remaining_photos = (
            db.query(Photo).filter(Photo.organization_id == org1.id).all()
        )

        # カスケード削除の場合は0、制約の場合は削除自体が失敗
        assert len(remaining_users) == 0
        assert len(remaining_photos) == 0
