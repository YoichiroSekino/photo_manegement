"""
Organizationモデルのテスト（マルチテナント対応）
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Organization


class TestOrganizationModel:
    """Organizationモデルのテスト"""

    @pytest.fixture
    def db(self):
        """テスト用のSQLiteデータベース"""
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        yield db
        db.close()

    def test_create_organization_success(self, db):
        """組織作成成功テスト"""
        org = Organization(name="Test Company", subdomain="testcompany", is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)

        assert org.id is not None
        assert org.name == "Test Company"
        assert org.subdomain == "testcompany"
        assert org.is_active is True
        assert isinstance(org.created_at, datetime)
        assert isinstance(org.updated_at, datetime)

    def test_organization_subdomain_unique(self, db):
        """サブドメインがユニークであることを確認"""
        org1 = Organization(name="Company A", subdomain="company")
        org2 = Organization(name="Company B", subdomain="company")  # 同じsubdomain

        db.add(org1)
        db.commit()

        db.add(org2)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_organization_default_is_active(self, db):
        """is_activeのデフォルト値がTrueであることを確認"""
        org = Organization(name="Test Org", subdomain="testorg")
        db.add(org)
        db.commit()
        db.refresh(org)

        assert org.is_active is True

    def test_organization_can_be_inactive(self, db):
        """is_activeをFalseに設定できることを確認"""
        org = Organization(name="Inactive Org", subdomain="inactive", is_active=False)
        db.add(org)
        db.commit()
        db.refresh(org)

        assert org.is_active is False

    def test_organization_repr(self, db):
        """__repr__メソッドのテスト"""
        org = Organization(name="Test Company", subdomain="testco")
        db.add(org)
        db.commit()
        db.refresh(org)

        repr_str = repr(org)
        assert "Organization" in repr_str
        assert str(org.id) in repr_str
        assert "testco" in repr_str

    def test_organization_updated_at_changes(self, db):
        """updated_atが更新時に変更されることを確認"""
        org = Organization(name="Update Test", subdomain="updatetest")
        db.add(org)
        db.commit()
        db.refresh(org)

        original_updated_at = org.updated_at

        # 少し待ってから更新
        import time

        time.sleep(0.01)

        org.name = "Updated Name"
        db.commit()
        db.refresh(org)

        # updated_atが変更されていることを確認
        assert org.updated_at != original_updated_at
        assert org.name == "Updated Name"

    def test_organization_name_required(self, db):
        """nameが必須であることを確認"""
        org = Organization(subdomain="noname")  # nameなし

        db.add(org)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_organization_subdomain_required(self, db):
        """subdomainが必須であることを確認"""
        org = Organization(name="No Subdomain")  # subdomainなし

        db.add(org)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()
