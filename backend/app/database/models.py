"""
SQLAlchemyデータベースモデル
工事写真管理システム
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    BigInteger,
    Float,
    Index,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import TypeDecorator

Base = declarative_base()


class Organization(Base):
    """組織テーブル（マルチテナント対応）"""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, subdomain='{self.subdomain}')>"


# テスト環境でTSVECTORをTextにフォールバックする型
class TSVECTORType(TypeDecorator):
    """PostgreSQL TSVECTORとSQLite Textの互換型"""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(TSVECTOR())
        else:
            # SQLiteやその他のDBではText型にフォールバック
            return dialect.type_descriptor(Text())


class Photo(Base):
    """写真テーブル"""

    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)

    # マルチテナント対応
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization = relationship("Organization")

    # プロジェクト関連
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    project = relationship("Project", back_populates="photos")

    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    s3_key = Column(String(500), nullable=False, unique=True)
    s3_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)

    # 写真情報
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    shooting_date = Column(DateTime, nullable=True)

    # 位置情報
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    location_address = Column(String(500), nullable=True)

    # カテゴリ情報
    major_category = Column(String(50), nullable=True)  # 写真-大分類
    photo_type = Column(String(100), nullable=True)  # 写真区分
    work_type = Column(String(100), nullable=True)  # 工種
    work_kind = Column(String(100), nullable=True)  # 種別
    work_detail = Column(String(100), nullable=True)  # 細別

    # メタデータ（JSONB）
    photo_metadata = Column("metadata", JSON, nullable=True)

    # タグ
    tags = Column(JSON, nullable=True)

    # OCR情報
    ocr_text = Column(Text, nullable=True)  # OCR抽出テキスト
    ocr_confidence = Column(Float, nullable=True)  # OCR信頼度（0.0-1.0）
    ocr_metadata = Column(JSON, nullable=True)  # OCR詳細メタデータ

    # 全文検索用（PostgreSQL TSVector / SQLite Text）
    search_vector = Column(TSVECTORType, nullable=True)

    # 重複検出用
    perceptual_hash = Column(String(64), nullable=True, index=True)  # 画像ハッシュ
    duplicate_group_id = Column(String(36), nullable=True, index=True)  # 重複グループID

    # 品質評価
    quality_score = Column(Integer, nullable=True)  # 品質スコア（0-100）
    quality_issues = Column(JSON, nullable=True)  # 品質問題の詳細

    # ステータス
    is_processed = Column(Boolean, default=False)
    is_representative = Column(Boolean, default=False)  # 代表写真
    is_submission_frequency = Column(Boolean, default=False)  # 提出頻度写真
    is_duplicate = Column(Boolean, default=False)  # 重複フラグ

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, file_name='{self.file_name}')>"


# GINインデックス（全文検索用）
Index("ix_photos_search_vector", Photo.search_vector, postgresql_using="gin")

# マルチテナント対応の複合インデックス
Index("ix_photos_org_created", Photo.organization_id, Photo.created_at)
Index("ix_photos_org_shooting_date", Photo.organization_id, Photo.shooting_date)


class User(Base):
    """ユーザーテーブル"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # マルチテナント対応
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization = relationship("Organization")

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class PhotoDuplicate(Base):
    """写真重複関係テーブル"""

    __tablename__ = "photo_duplicates"

    id = Column(Integer, primary_key=True, index=True)

    # マルチテナント対応
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization = relationship("Organization")

    photo1_id = Column(Integer, ForeignKey("photos.id"), nullable=False, index=True)
    photo2_id = Column(Integer, ForeignKey("photos.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)  # 類似度スコア（0.0-1.0）
    duplicate_type = Column(
        String(50), nullable=True
    )  # 重複タイプ（exact, similar, etc.）
    status = Column(
        String(20), default="pending", nullable=False
    )  # pending, confirmed, rejected
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<PhotoDuplicate(id={self.id}, photo1_id={self.photo1_id}, photo2_id={self.photo2_id}, similarity={self.similarity_score})>"


class Project(Base):
    """プロジェクトテーブル"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # マルチテナント対応
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization = relationship("Organization")

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    client_name = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # 写真との関連
    photos = relationship("Photo", back_populates="project")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
