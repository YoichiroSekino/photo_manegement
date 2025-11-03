"""
プロジェクトAPIのテスト
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import get_db
from app.database.models import User, Organization, Project, Photo, Base
from app.auth.dependencies import get_current_active_user

# テスト用のSQLiteデータベース
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_projects.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """テスト用データベースセッション"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_org(db):
    """テスト用組織"""
    org = Organization(name="Test Org", subdomain="test", is_active=True)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_user(db, test_org):
    """テスト用ユーザー"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        organization_id=test_org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client(db, test_user):
    """テストクライアント"""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_active_user] = lambda: test_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_project(client, test_user):
    """プロジェクト作成のテスト"""
    project_data = {
        "name": "Test Project",
        "description": "Test Description",
        "client_name": "Test Client",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
    }

    response = client.post("/api/v1/projects", json=project_data)
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert data["client_name"] == "Test Client"
    assert data["organization_id"] == test_user.organization_id
    assert data["photo_count"] == 0
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_minimal(client, test_user):
    """最小限のデータでプロジェクト作成"""
    project_data = {"name": "Minimal Project"}

    response = client.post("/api/v1/projects", json=project_data)
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Minimal Project"
    assert data["description"] is None
    assert data["client_name"] is None
    assert data["start_date"] is None
    assert data["end_date"] is None


def test_list_projects(client, db, test_user):
    """プロジェクト一覧取得のテスト"""
    # テストデータ作成
    for i in range(3):
        project = Project(
            name=f"Project {i}",
            organization_id=test_user.organization_id,
        )
        db.add(project)
    db.commit()

    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    # プロジェクト名のセットを確認（順序は問わない）
    project_names = {p["name"] for p in data}
    assert project_names == {"Project 0", "Project 1", "Project 2"}


def test_list_projects_pagination(client, db, test_user):
    """プロジェクト一覧ページネーションのテスト"""
    # テストデータ作成
    for i in range(5):
        project = Project(
            name=f"Project {i}",
            organization_id=test_user.organization_id,
        )
        db.add(project)
    db.commit()

    # 1ページ目（2件）
    response = client.get("/api/v1/projects?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # 2ページ目（2件）
    response = client.get("/api/v1/projects?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # 3ページ目（1件）
    response = client.get("/api/v1/projects?skip=4&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_project(client, db, test_user):
    """プロジェクト詳細取得のテスト"""
    # テストデータ作成
    project = Project(
        name="Test Project",
        description="Test Description",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    response = client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == project.id
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert data["photo_count"] == 0


def test_get_project_not_found(client):
    """存在しないプロジェクトの取得"""
    response = client.get("/api/v1/projects/99999")
    assert response.status_code == 404


def test_get_project_different_organization(client, db, test_user):
    """別組織のプロジェクトにアクセス（403）"""
    # 別組織作成
    other_org = Organization(name="Other Org", subdomain="other", is_active=True)
    db.add(other_org)
    db.commit()

    # 別組織のプロジェクト作成
    other_project = Project(
        name="Other Project",
        organization_id=other_org.id,
    )
    db.add(other_project)
    db.commit()
    db.refresh(other_project)

    # アクセス試行
    response = client.get(f"/api/v1/projects/{other_project.id}")
    assert response.status_code == 403


def test_update_project(client, db, test_user):
    """プロジェクト更新のテスト"""
    # テストデータ作成
    project = Project(
        name="Original Name",
        description="Original Description",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 更新
    update_data = {
        "name": "Updated Name",
        "description": "Updated Description",
        "client_name": "New Client",
    }

    response = client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Description"
    assert data["client_name"] == "New Client"


def test_update_project_partial(client, db, test_user):
    """プロジェクト部分更新のテスト"""
    # テストデータ作成
    project = Project(
        name="Original Name",
        description="Original Description",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 名前のみ更新
    update_data = {"name": "Updated Name"}

    response = client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Original Description"  # 変更なし


def test_delete_project(client, db, test_user):
    """プロジェクト削除のテスト（写真なし）"""
    # テストデータ作成
    project = Project(
        name="To Delete",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 削除
    response = client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 204

    # 削除確認
    response = client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 404


def test_delete_project_with_photos(client, db, test_user):
    """写真が紐づいているプロジェクトの削除（RESTRICT動作）"""
    # テストデータ作成
    project = Project(
        name="Project with Photos",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 写真を追加
    photo = Photo(
        organization_id=test_user.organization_id,
        project_id=project.id,
        file_name="test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        s3_key="test/test.jpg",
    )
    db.add(photo)
    db.commit()

    # 削除試行（失敗するはず）
    response = client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 400
    assert "写真が紐づいている" in response.json()["detail"]


def test_get_project_photos(client, db, test_user):
    """プロジェクトの写真一覧取得のテスト"""
    # テストデータ作成
    project = Project(
        name="Test Project",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 写真を追加
    for i in range(3):
        photo = Photo(
            organization_id=test_user.organization_id,
            project_id=project.id,
            file_name=f"test{i}.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key=f"test/test{i}.jpg",
        )
        db.add(photo)
    db.commit()

    response = client.get(f"/api/v1/projects/{project.id}/photos")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert all("file_name" in photo for photo in data)


def test_get_project_stats(client, db, test_user):
    """プロジェクト統計情報取得のテスト"""
    # テストデータ作成
    project = Project(
        name="Test Project",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 写真を追加（異なるカテゴリ）
    for i in range(5):
        photo = Photo(
            organization_id=test_user.organization_id,
            project_id=project.id,
            file_name=f"test{i}.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key=f"test/test{i}.jpg",
            major_category="施工状況写真" if i < 3 else "完成写真",
            quality_score=80 if i < 4 else 50,  # 1枚は品質問題
        )
        db.add(photo)
    db.commit()

    response = client.get(f"/api/v1/projects/{project.id}/stats")
    assert response.status_code == 200
    data = response.json()

    assert data["project_id"] == project.id
    assert data["photo_count"] == 5
    assert data["quality_issues_count"] == 1
    assert "施工状況写真" in data["category_distribution"]
    assert data["category_distribution"]["施工状況写真"] == 3
    assert data["category_distribution"]["完成写真"] == 2


def test_project_with_photo_count(client, db, test_user):
    """photo_countが正しく計算されるテスト"""
    # テストデータ作成
    project = Project(
        name="Test Project",
        organization_id=test_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 写真を追加
    for i in range(10):
        photo = Photo(
            organization_id=test_user.organization_id,
            project_id=project.id,
            file_name=f"test{i}.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            s3_key=f"test/test{i}.jpg",
        )
        db.add(photo)
    db.commit()

    response = client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["photo_count"] == 10
