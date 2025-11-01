"""
Pydanticスキーマのテスト
"""

import pytest
from datetime import datetime
from app.schemas.photo import PhotoCreate, PhotoResponse, PhotoCategory


def test_photo_create_schema():
    """PhotoCreateスキーマのテスト"""
    data = {
        "file_name": "test.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/test.jpg",
    }
    photo = PhotoCreate(**data)

    assert photo.file_name == "test.jpg"
    assert photo.file_size == 1024000
    assert photo.mime_type == "image/jpeg"
    assert photo.s3_key == "photos/test.jpg"


def test_photo_create_with_optional_fields():
    """オプションフィールドを含むPhotoCreateのテスト"""
    data = {
        "file_name": "test.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/test.jpg",
        "title": "テスト写真",
        "description": "これはテストです",
        "shooting_date": datetime(2024, 3, 15),
    }
    photo = PhotoCreate(**data)

    assert photo.title == "テスト写真"
    assert photo.description == "これはテストです"
    assert photo.shooting_date.year == 2024


def test_photo_response_schema():
    """PhotoResponseスキーマのテスト"""
    data = {
        "id": 1,
        "file_name": "test.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "s3_key": "photos/test.jpg",
        "s3_url": "https://example.com/test.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    photo = PhotoResponse(**data)

    assert photo.id == 1
    assert photo.file_name == "test.jpg"
    assert photo.s3_url == "https://example.com/test.jpg"


def test_photo_category_schema():
    """PhotoCategoryスキーマのテスト"""
    data = {
        "major_category": "工事",
        "photo_type": "施工状況写真",
        "work_type": "土工",
    }
    category = PhotoCategory(**data)

    assert category.major_category == "工事"
    assert category.photo_type == "施工状況写真"
    assert category.work_type == "土工"


def test_invalid_mime_type():
    """無効なMIMEタイプのテスト"""
    data = {
        "file_name": "test.png",
        "file_size": 1024000,
        "mime_type": "image/png",  # PNGは無効
        "s3_key": "photos/test.png",
    }

    with pytest.raises(ValueError):
        PhotoCreate(**data)
