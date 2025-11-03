"""Dashboard API tests."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import Photo, Project


@pytest.fixture
def test_project(db, test_org):
    """Test project fixture."""
    project = Project(
        organization_id=test_org.id,
        name="Test Project",
        description="Test project",
        
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_get_dashboard_stats_unauthenticated(client: TestClient):
    """Test getting dashboard stats without authentication."""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 403  # Tenant middleware returns 403


def test_get_dashboard_stats_empty(
    client: TestClient, db: Session, auth_headers: dict
):
    """Test getting dashboard stats with no photos."""
    response = client.get("/api/v1/dashboard/stats", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_photos"] == 0
    assert data["today_uploads"] == 0
    assert data["this_week_uploads"] == 0
    assert data["duplicates_count"] == 0
    assert data["quality_issues_count"] == 0
    assert data["category_distribution"] == {}


def test_get_dashboard_stats_with_data(
    client: TestClient, db: Session, auth_headers: dict, test_org, test_project
):
    """Test getting dashboard stats with sample data."""
    # Create photos with various attributes
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    # Today's upload
    photo1 = Photo(
        file_name="P0000001.JPG",
        file_size=1024000,
        mime_type="image/jpeg",
        s3_key="photos/P0000001.JPG",
        organization_id=test_org.id,
        project_id=test_project.id,
        title="Today Photo",
        major_category="施工状況写真",
        shooting_date=today.date(),
        quality_score=80,
        created_at=today,
    )

    # Yesterday's upload (this week)
    photo2 = Photo(
        file_name="P0000002.JPG",
        file_size=1024000,
        mime_type="image/jpeg",
        s3_key="photos/P0000002.JPG",
        organization_id=test_org.id,
        project_id=test_project.id,
        title="Yesterday Photo",
        major_category="施工状況写真",
        shooting_date=yesterday.date(),
        quality_score=90,
        created_at=yesterday,
    )

    # Last week's upload
    photo3 = Photo(
        file_name="P0000003.JPG",
        file_size=1024000,
        mime_type="image/jpeg",
        s3_key="photos/P0000003.JPG",
        organization_id=test_org.id,
        project_id=test_project.id,
        title="Last Week Photo",
        major_category="安全管理写真",
        shooting_date=last_week.date(),
        quality_score=30,  # Quality issue
        created_at=last_week,
    )

    # Duplicate photos
    photo4 = Photo(
        file_name="P0000004.JPG",
        file_size=1024000,
        mime_type="image/jpeg",
        s3_key="photos/P0000004.JPG",
        organization_id=test_org.id,
        project_id=test_project.id,
        title="Duplicate 1",
        major_category="品質管理写真",
        shooting_date=today.date(),
        quality_score=70,
        duplicate_group_id="group1",
        created_at=today,
    )

    photo5 = Photo(
        file_name="P0000005.JPG",
        file_size=1024000,
        mime_type="image/jpeg",
        s3_key="photos/P0000005.JPG",
        organization_id=test_org.id,
        project_id=test_project.id,
        title="Duplicate 2",
        major_category="品質管理写真",
        shooting_date=today.date(),
        quality_score=70,
        duplicate_group_id="group1",
        created_at=today,
    )

    db.add_all([photo1, photo2, photo3, photo4, photo5])
    db.commit()

    response = client.get("/api/v1/dashboard/stats", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_photos"] == 5
    assert data["today_uploads"] == 3  # photo1, photo4, photo5
    # This week uploads depends on the current day of the week
    assert data["this_week_uploads"] >= 3
    assert data["duplicates_count"] == 1  # One duplicate group
    assert data["quality_issues_count"] == 1  # photo3 has quality < 50

    # Category distribution
    assert data["category_distribution"]["施工状況写真"] == 2
    assert data["category_distribution"]["安全管理写真"] == 1
    assert data["category_distribution"]["品質管理写真"] == 2


def test_get_recent_photos_unauthenticated(client: TestClient):
    """Test getting recent photos without authentication."""
    response = client.get("/api/v1/dashboard/recent-photos")
    assert response.status_code == 403  # Tenant middleware returns 403


def test_get_recent_photos_empty(
    client: TestClient, db: Session, auth_headers: dict
):
    """Test getting recent photos with no data."""
    response = client.get("/api/v1/dashboard/recent-photos", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_recent_photos_with_data(
    client: TestClient, db: Session, auth_headers: dict, test_org, test_project
):
    """Test getting recent photos with sample data."""
    # Create 10 photos
    photos = []
    for i in range(10):
        photo = Photo(
            file_name=f"P{i:07d}.JPG",
            file_size=1024000,
            mime_type="image/jpeg",
            s3_key=f"photos/P{i:07d}.JPG",
            organization_id=test_org.id,
            project_id=test_project.id,
            title=f"Photo {i}",
            major_category="施工状況写真",
            shooting_date=datetime.utcnow().date(),
            quality_score=80,
            created_at=datetime.utcnow() - timedelta(minutes=i),
        )
        photos.append(photo)

    db.add_all(photos)
    db.commit()

    # Test default limit (6)
    response = client.get("/api/v1/dashboard/recent-photos", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6

    # Verify photos are sorted by created_at descending
    assert data[0]["file_name"] == "P0000000.JPG"  # Most recent
    assert data[5]["file_name"] == "P0000005.JPG"

    # Verify response structure
    assert "id" in data[0]
    assert "file_name" in data[0]
    assert "s3_key" in data[0]
    assert "title" in data[0]
    assert "major_category" in data[0]
    assert "shooting_date" in data[0]
    assert "quality_score" in data[0]
    assert "created_at" in data[0]


def test_get_recent_photos_custom_limit(
    client: TestClient, db: Session, auth_headers: dict, test_org, test_project
):
    """Test getting recent photos with custom limit."""
    # Create 10 photos
    photos = []
    for i in range(10):
        photo = Photo(
            file_name=f"P{i:07d}.JPG",
            file_size=1024000,
            mime_type="image/jpeg",
            s3_key=f"photos/P{i:07d}.JPG",
            organization_id=test_org.id,
            project_id=test_project.id,
            title=f"Photo {i}",
            major_category="施工状況写真",
            shooting_date=datetime.utcnow().date(),
            quality_score=80,
            created_at=datetime.utcnow() - timedelta(minutes=i),
        )
        photos.append(photo)

    db.add_all(photos)
    db.commit()

    # Test custom limit
    response = client.get(
        "/api/v1/dashboard/recent-photos?limit=3", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["file_name"] == "P0000000.JPG"
    assert data[2]["file_name"] == "P0000002.JPG"
