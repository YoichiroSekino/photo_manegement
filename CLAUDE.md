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

### Recommended Tech Stack

**Frontend**:
- Next.js 14+ (App Router)
- TypeScript
- Material-UI or Tailwind CSS
- Redux Toolkit or Zustand for state management
- Google Maps API or Mapbox for location features

**Backend**:
- Node.js + Express OR FastAPI (Python)
- AWS Lambda for serverless functions
- PostgreSQL + Redis
- Elasticsearch for search

**AI/ML**:
- Amazon Rekognition (image recognition)
- Amazon Textract (OCR for blackboard reading)
- TensorFlow/PyTorch for custom models

**Infrastructure** (AWS):
- S3 (storage) + CloudFront (CDN)
- Lambda (compute)
- RDS PostgreSQL (metadata)
- SageMaker (ML)
- API Gateway
- SQS (async processing queue)

### Performance Targets

- Concurrent upload: 10,000 photos
- Processing time per photo: <2 seconds (including AI classification)
- Search response: <500ms
- Concurrent users: 1,000
- Availability: 99.9%

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

(To be added as the project develops)

## Important Notes

- **Photo authenticity is critical** - Implement EXIF validation to detect editing
- **Character encoding matters** - Always use Shift_JIS for PHOTO.XML
- **File naming is strict** - Validate against regex: `^P[0-9]{7}\.JPG$`
- **Date format is fixed** - CCYY-MM-DD (e.g., 2024-03-15), not YYYY-MM-DD in documentation
- **Blackboard OCR** - Expect ~85-90% accuracy, provide manual correction UI
- **Scale planning** - Design for 200,000 photos per project from day one
