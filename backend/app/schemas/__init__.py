"""
Pydanticスキーマモジュール
"""

from app.schemas.photo import (
    PhotoCreate,
    PhotoUpdate,
    PhotoResponse,
    PhotoListResponse,
    PhotoCategory,
)
from app.schemas.search import SearchQuery, SearchResponse
from app.schemas.rekognition import (
    ImageLabelResponse,
    ClassificationResponse,
    ClassificationResultResponse,
)
from app.schemas.duplicate import (
    PhotoHashInfo,
    DuplicatePhotoInfo,
    DuplicateGroupResponse,
    DuplicateDetectionResponse,
    CalculateHashResponse,
)

__all__ = [
    "PhotoCreate",
    "PhotoUpdate",
    "PhotoResponse",
    "PhotoListResponse",
    "PhotoCategory",
    "SearchQuery",
    "SearchResponse",
    "ImageLabelResponse",
    "ClassificationResponse",
    "ClassificationResultResponse",
    "PhotoHashInfo",
    "DuplicatePhotoInfo",
    "DuplicateGroupResponse",
    "DuplicateDetectionResponse",
    "CalculateHashResponse",
]
