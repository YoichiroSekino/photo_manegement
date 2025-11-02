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
from app.schemas.quality import (
    QualityMetrics,
    QualityAssessmentResponse,
    QualityCheckResponse,
)
from app.schemas.title import (
    TitleGenerationRequest,
    TitleGenerationResponse,
    TitleUpdateRequest,
)
from app.schemas.photo_xml import (
    PhotoXMLGenerationRequest,
    PhotoXMLGenerationResponse,
    PhotoXMLValidationResponse,
)
from app.schemas.export import (
    ExportRequest,
    ExportResponse,
    ExportValidationResponse,
    FileRenameInfo,
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
    "QualityMetrics",
    "QualityAssessmentResponse",
    "QualityCheckResponse",
    "TitleGenerationRequest",
    "TitleGenerationResponse",
    "TitleUpdateRequest",
    "PhotoXMLGenerationRequest",
    "PhotoXMLGenerationResponse",
    "PhotoXMLValidationResponse",
    "ExportRequest",
    "ExportResponse",
    "ExportValidationResponse",
    "FileRenameInfo",
]
