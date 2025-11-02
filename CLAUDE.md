# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Construction Photo Management System (工事写真自動整理システム) - An AI-powered system for automatically organizing and managing construction site photos (up to 200,000 images) in compliance with Japan's MLIT "Digital Photo Management Information Standards" (令和5年3月版).

## Critical Compliance Requirements

### Digital Photo Management Standards (デジタル写真管理情報基準)

1. **Photo File Naming Convention** (MUST be strictly followed):
   - Photo files: `Pnnnnnnn.JPG` (e.g., P0000001.JPG)
   - Reference drawings: `Dnnnnnnn.XXX` (e.g., D0000001.JPG)
   - P/D prefix is FIXED, followed by 7-digit serial number

2. **File Format Requirements**:
   - Acceptable formats: JPEG, TIFF, SVG (SVG requires supervisor approval)
   - Compression: JPEG standard (~1/16 compression ratio)
   - **NO EDITING ALLOWED** - Photos must NOT be edited (brightness, cropping, rotation, etc.) to maintain authenticity

3. **Image Quality Standards**:
   - Minimum: 1,000,000 pixels (100万画素)
   - Recommended: 2,000,000 pixels (200万画素) - 1600×1200
   - Maximum: 3,000,000 pixels (300万画素)
   - Blackboard text MUST be readable

4. **PHOTO.XML Generation** (PHOTO05.DTD compliance):
   - Encoding: Shift_JIS
   - DTD version: PHOTO05
   - Standard code: 土木202303-01
   - XML declaration: `<?xml version="1.0" encoding="Shift_JIS"?>`

5. **Directory Structure** (electronic delivery):
   ```
   PHOTO/
   ├── PHOTO.XML
   ├── PHOTO05.DTD
   ├── PHOTO05.XSL (optional)
   ├── PIC/          # Photo files
   │   └── P*.JPG
   └── DRA/          # Reference drawings (optional)
       └── D*.JPG
   ```

6. **Photo Categories** (写真区分):
   - 着手前及び完成写真 (Before/after photos)
   - 施工状況写真 (Construction progress)
   - 安全管理写真 (Safety management)
   - 使用材料写真 (Materials used)
   - 品質管理写真 (Quality control)
   - 出来形管理写真 (Completion status)
   - 災害写真 (Disaster)
   - 事故写真 (Accident)
   - その他 (Others)

7. **Required Metadata Fields** (◎ = mandatory):
   - 写真フォルダ名 (max 9 chars, uppercase alphanumeric)
   - 適用要領基準 (standard code)
   - シリアル番号 (7 digits)
   - 写真ファイル名 (12 chars)
   - メディア番号
   - 写真-大分類 (major category)
   - 写真タイトル (max 127 chars)
   - 撮影年月日 (CCYY-MM-DD format)
   - 代表写真 (representative photo flag)
   - 提出頻度写真 (submission frequency flag)

8. **Character Set Restrictions**:
   - Folder/file names: Half-width uppercase alphanumeric only
   - Japanese text: JIS X 0208 compliant (NO half-width katakana)
   - Date format: CCYY-MM-DD (fixed)

## Architecture

### Current Implementation

**Frontend:**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand stores (uploadStore, filterStore, uiStore)
- **Data Fetching**: TanStack React Query v5
- **Testing**: Jest + React Testing Library
- **Key Directories**:
  - `src/app/` - Next.js pages (upload, photos, search, duplicates, quality, export, login)
  - `src/components/` - Reusable UI components organized by feature
  - `src/hooks/` - Custom React hooks (usePhotos for photo operations)
  - `src/lib/` - Utilities (apiClient, s3Upload, fileValidator, queryClient)
  - `src/store/` - Zustand state stores
  - `src/contexts/` - React contexts (AuthContext)

**Backend:**
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy with Alembic migrations
- **Database**: PostgreSQL 15 (production), SQLite (tests)
- **Testing**: pytest with 80% coverage
- **Architecture Pattern**: Layered (routers → services → database)
- **Key Modules**:
  - `app/routers/` - API endpoints (photos, search, ocr, rekognition, duplicate, quality, title, export, photo_xml, photo_album)
  - `app/services/` - Business logic (OCR, image classification, duplicate detection, quality assessment, title generation, export, XML/PDF generation)
  - `app/schemas/` - Pydantic models for request/response validation
  - `app/database/` - SQLAlchemy models and database connection
  - `app/auth/` - JWT authentication and authorization

**AI/ML Services (AWS):**
- **OCR**: Amazon Textract for blackboard text extraction
- **Image Classification**: Amazon Rekognition for photo categorization
- **Hash-based Duplicate Detection**: Perceptual hashing (pHash) using imagehash library
- **Quality Assessment**: OpenCV for blur detection and quality scoring

**Database Schema:**
- **photos**: Main photo table with metadata, OCR results, AI labels, quality scores
  - `search_vector`: PostgreSQL TSVECTOR for full-text search (with SQLite fallback)
  - Indexes: GIN index on search_vector, perceptual_hash, duplicate_group_id
- **photo_duplicates**: Many-to-many relationship for duplicate photos
- **users**: Authentication and user management
- **projects**: Project/construction site grouping

**Cross-Database Compatibility:**
- `TSVECTORType`: Custom TypeDecorator that uses TSVECTOR for PostgreSQL and Text for SQLite
- Search router detects database dialect and switches between full-text search (PostgreSQL) and LIKE queries (SQLite)

### Performance Targets

- Concurrent upload: 10,000 photos
- Processing time per photo: <2 seconds (including AI classification)
- Search response: <500ms
- Concurrent users: 1,000
- Availability: 99.9%

### Data Flow

1. **Photo Upload Flow**:
   ```
   Frontend (DragDropZone)
   → Presigned URL request (POST /api/v1/photos/upload)
   → S3 Direct Upload
   → Photo metadata creation (POST /api/v1/photos)
   → Background processing (OCR, Rekognition, Quality)
   ```

2. **Search Flow**:
   ```
   Frontend (SearchBar/FilterPanel)
   → GET /api/v1/photos/search?keyword=X&work_type=Y
   → Database query with TSVECTOR (PostgreSQL) or LIKE (SQLite)
   → Paginated results
   ```

3. **Export Flow**:
   ```
   Frontend → POST /api/v1/export/photo-xml
   → PhotoXMLGenerator service
   → PHOTO.XML generation (PHOTO05.DTD, Shift_JIS)
   → ZIP package creation
   → Download response
   ```

## Key Features to Implement

1. **Bulk Photo Upload**: Drag-and-drop, multipart upload to S3, progress tracking
2. **OCR for Blackboards** (黒板OCR): Extract construction info from site boards
3. **AI Auto-Classification**: Categorize photos by construction phase/type
4. **Location Management**: GPS-based mapping and area search
5. **Duplicate Detection**: Image hash-based similarity detection
6. **Quality Validation**: Check pixel count, file naming, metadata completeness
7. **PHOTO.XML Generation**: Compliant with PHOTO05.DTD
8. **Photo Album Creation**: PDF/Excel/Word export
9. **Search/Filter**: By location, date, category, keywords

## Validation Requirements

When implementing validation logic:

```typescript
interface PhotoValidation {
  fileNaming: boolean;      // Pnnnnnnn.JPG format
  pixelCount: boolean;      // 1M-3M pixels
  fileFormat: boolean;      // JPEG/TIFF/SVG
  noEditing: boolean;       // EXIF integrity check
  blackboardReadable: boolean; // OCR confidence check
  metadataComplete: boolean;   // All required fields
  characterLimits: boolean;    // Field length constraints
}
```

## API Structure

RESTful endpoints to implement:

- `POST /api/v1/photos/upload` - Bulk photo upload
- `GET /api/v1/photos/search` - Search with filters
- `POST /api/v1/export/photo-xml` - Generate PHOTO.XML
- `POST /api/v1/webhooks` - Webhook notifications

## Security

- Authentication: AWS Cognito or Auth0
- Encryption: At rest (S3) and in transit (HTTPS)
- Access control: Role-based (RBAC)
- Audit logs: All operations tracked
- Compliance: GDPR/personal data protection

## Development Commands

### Backend (FastAPI + Python)

**Setup:**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

**Run Development Server:**
```bash
cd backend
./venv/Scripts/activate  # Windows
uvicorn app.main:app --reload
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Database Migrations:**
```bash
cd backend
# Create new migration
./venv/Scripts/alembic revision --autogenerate -m "description"
# Apply migrations
./venv/Scripts/alembic upgrade head
# Rollback
./venv/Scripts/alembic downgrade -1
```

**Testing:**
```bash
cd backend
# Run all tests
./venv/Scripts/pytest
# Run with coverage
./venv/Scripts/pytest --cov=app --cov-report=term-missing
# Run specific test file
./venv/Scripts/pytest tests/test_api_photos.py
# Run specific test
./venv/Scripts/pytest tests/test_api_photos.py::test_create_photo -v
```

**Linting & Formatting:**
```bash
cd backend
# Format code
./venv/Scripts/black app tests
# Lint
./venv/Scripts/pylint app
# Type check
./venv/Scripts/mypy app
```

### Frontend (Next.js 14 + TypeScript)

**Setup:**
```bash
cd frontend
npm install
```

**Run Development Server:**
```bash
cd frontend
npm run dev
# Server runs at http://localhost:3000
```

**Testing:**
```bash
cd frontend
# Run tests in watch mode
npm test
# Run all tests once with coverage
npm run test:ci
# Run specific test file
npm test -- src/lib/__tests__/apiClient.test.ts
```

**Build & Type Check:**
```bash
cd frontend
# Type check
npm run type-check
# Production build
npm run build
# Run production server
npm start
```

### Docker Environment

**Start all services:**
```bash
docker-compose up -d
# PostgreSQL: localhost:5432
# Redis: localhost:6379
# pgAdmin: http://localhost:5050 (admin@example.com / admin)
```

**Stop services:**
```bash
docker-compose down
# Remove volumes (clears data)
docker-compose down -v
```

**View logs:**
```bash
docker-compose logs -f postgres
docker-compose logs -f redis
```

## Testing Strategy (TDD)

This project strictly follows **Test-Driven Development (Red-Green-Refactor)**.

### Backend Testing

**Current Coverage**: 80% (141 tests)

**Test Structure:**
- Unit tests for all services (`test_*_service.py`)
- API endpoint tests (`test_api_*.py`)
- Schema validation tests (`test_schemas.py`)

**Key Testing Patterns:**

1. **Database Testing**:
   ```python
   @pytest.fixture
   def db():
       """SQLite in-memory database for fast tests"""
       engine = create_engine("sqlite:///:memory:")
       TestingSessionLocal = sessionmaker(bind=engine)
       Base.metadata.create_all(bind=engine)
       # ...
   ```

2. **Mock AWS Services**:
   ```python
   @patch("boto3.client")
   def test_ocr_service(mock_boto_client):
       mock_textract = Mock()
       mock_textract.detect_document_text.return_value = {...}
       mock_boto_client.return_value = mock_textract
   ```

3. **Cross-Database Compatibility**:
   - Tests run on SQLite for speed
   - Production uses PostgreSQL with TSVECTOR
   - `TSVECTORType` provides compatibility layer
   - Search router detects dialect and adjusts queries

### Frontend Testing

**Current Coverage**: 12.22% (45 tests) - **Target: 60%**

**Test Files:**
- Component tests: `components/**/__tests__/*.test.tsx`
- Hook tests: `hooks/__tests__/*.test.ts`
- Utility tests: `lib/__tests__/*.test.ts`

**Key Testing Patterns:**

1. **API Client Mocking**:
   ```typescript
   global.fetch = jest.fn();
   (global.fetch as jest.Mock).mockResolvedValue({
     ok: true,
     json: async () => ({ id: 1, name: 'Test' })
   });
   ```

2. **Component Testing**:
   ```typescript
   import { render, screen, fireEvent } from '@testing-library/react';

   test('PhotoCard displays photo information', () => {
     render(<PhotoCard photo={mockPhoto} />);
     expect(screen.getByText('test.jpg')).toBeInTheDocument();
   });
   ```

3. **Concurrent Operations**:
   ```typescript
   // Pattern for testing Promise.all with mocks
   let callCount = 0;
   (global.fetch as jest.Mock).mockImplementation(async () => {
     const currentCount = ++callCount;  // Capture immediately
     return { ok: true, json: async () => ({ key: `key${currentCount}` }) };
   });
   ```

### TDD Workflow

1. **Write failing test** (Red)
2. **Implement minimum code to pass** (Green)
3. **Refactor while keeping tests green** (Refactor)

**Example from this project:**
```bash
# 1. Write test for search filter
# tests/test_api_search.py::test_search_by_major_category

# 2. Run test (should fail)
pytest tests/test_api_search.py::test_search_by_major_category

# 3. Implement feature in app/routers/search.py
# if major_category:
#     query = query.filter(Photo.major_category == major_category)

# 4. Run test again (should pass)
pytest tests/test_api_search.py::test_search_by_major_category

# 5. Refactor if needed
```

## Important Notes

- **Photo authenticity is critical** - Implement EXIF validation to detect editing
- **Character encoding matters** - Always use Shift_JIS for PHOTO.XML
- **File naming is strict** - Validate against regex: `^P[0-9]{7}\.JPG$`
- **Date format is fixed** - CCYY-MM-DD (e.g., 2024-03-15), not YYYY-MM-DD in documentation
- **Blackboard OCR** - Expect ~85-90% accuracy, provide manual correction UI
- **Scale planning** - Design for 200,000 photos per project from day one
- **TDD is mandatory** - Write tests before implementation (Red-Green-Refactor cycle)
- **Database compatibility** - Tests use SQLite, production uses PostgreSQL. Use `TSVECTORType` for full-text search compatibility
