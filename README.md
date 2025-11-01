# 工事写真自動整理システム (Construction Photo Management System)

**Phase 1 MVP リリース完了！** 🎉 (v0.1.0 - 2025-11-02)

[![Tests](https://img.shields.io/badge/tests-32%20passed-success)](./backend/tests)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](./backend/htmlcov)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue)](https://www.typescriptlang.org/)

> **最新情報**: Phase 1 (Week 1-10) が完了しました。写真管理、OCR処理、検索機能が実装され、TDDに基づく高品質なコードベース（97%カバレッジ）を確立しました。詳細は [PHASE1_RELEASE.md](./PHASE1_RELEASE.md) をご覧ください。

## 🚀 クイックスタート

```bash
# 1. Docker環境起動
docker-compose up -d

# 2. バックエンド起動
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload

# 3. フロントエンド起動（別ターミナル）
cd frontend && npm install && npm run dev

# アクセス
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

詳細は [SETUP.md](./SETUP.md) を参照

## 📊 Phase 1 実装状況

| 機能 | ステータス | テスト | カバレッジ |
|------|-----------|--------|-----------|
| ✅ 写真管理API | 完了 | 4/4 | 100% |
| ✅ OCR処理（Textract） | 完了 | 11/11 | 96% |
| ✅ 検索機能 | 完了 | 9/9 | 95% |
| ✅ データベース設計 | 完了 | - | 100% |
| ✅ フロントエンド基盤 | 完了 | 19/19 | 100% |
| 🔄 S3アップロード | Phase 2 | - | - |
| 🔄 画像分類AI | Phase 2 | - | - |
| 🔄 電子納品XML | Phase 3 | - | - |

## 開発方針
- 最重要：ドキュメントやGithubのコメントは日本語を使う
- docsに格納されているドキュメントを読み込みシステム開発計画書を作成する
- システム開発計画書に基づいたタスクを Github issuesを作成する
- issuesにかかる工数は5人日（40時間）を最大とし、極力1人日単位でまとめる
- issuesを順次実行する
- **テスト駆動開発（TDD）を厳格に採用** ← Phase 1で97%カバレッジ達成！

## 📋 概要

建設現場で撮影される大量の工事写真（数万～20万枚）をAIで自動的に整理・分類し、国土交通省の「デジタル写真管理情報基準」に準拠した形で管理するシステムです。

### 主な特徴

- 🤖 **AI自動分類**: 画像認識とOCRによる自動整理
- 📍 **位置情報管理**: GPS情報による地図表示と検索
- 📅 **時系列管理**: 撮影日時による絞り込みと整理
- 📝 **自動タイトル生成**: 工事黒板の情報から自動でタイトル付与
- 📊 **電子納品対応**: PHOTO.XML自動生成
- 📚 **写真帳作成**: 工事写真帳の自動生成

## 🎯 解決する課題

1. **膨大な写真整理の工数削減** - 従来の手作業による分類・整理作業を90%以上削減
2. **写真管理基準への準拠** - 国土交通省「デジタル写真管理情報基準（令和5年3月版）」に完全準拠
3. **必要な写真の迅速な検索** - 位置・日時・工種から瞬時に検索
4. **重複・不良写真の排除** - AIによる自動品質チェック
5. **電子納品作業の効率化** - PHOTO.XML（PHOTO05.DTD準拠）自動生成による納品準備時間の短縮

## 📚 準拠基準

本システムは以下の基準に完全準拠しています：
- **国土交通省「デジタル写真管理情報基準」令和5年3月版**
- **適用要領基準コード**: 土木202303-01
- **DTDバージョン**: PHOTO05.DTD

## 🏗️ システムアーキテクチャ

### 推奨構成（ベストプラクティス）

```
┌─────────────────────────────────────────────────────────┐
│                     フロントエンド層                      │
│  React/Next.js + TypeScript (Progressive Web App)        │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                      API Gateway                         │
│                    (AWS API Gateway)                     │
└─────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────┬────────────────┬─────────────────┐
│  写真アップロード     │   AI処理       │  データ管理      │
│  Lambda + S3         │  SageMaker/    │  Lambda + RDS    │
│  (並列処理)          │  Rekognition   │  (PostgreSQL)    │
└──────────────────────┴────────────────┴─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                    ストレージ層                          │
│   S3 (原本保管) + CloudFront (配信最適化)                │
└─────────────────────────────────────────────────────────┘
```

### パフォーマンス最適化戦略

1. **大量アップロード対応**
   - マルチパートアップロード（S3 Multipart Upload）
   - 並列処理による高速化（AWS Lambda並列実行）
   - プログレッシブアップロード（断片化アップロード）

2. **AI処理の最適化**
   - バッチ処理とリアルタイム処理の使い分け
   - 処理優先度による非同期キュー管理（SQS）
   - エッジAI処理の活用（軽量な前処理）

3. **検索・表示の高速化**
   - ElasticSearchによる全文検索
   - CloudFrontによるCDN配信
   - サムネイル事前生成とキャッシング

## 🚀 主要機能

### 1. 写真アップロード・取り込み

- **大量一括アップロード**: ドラッグ&ドロップで最大10,000枚同時処理
- **フォルダ構造維持**: 既存のフォルダ階層を保持したままインポート
- **断点続行**: アップロード中断時の自動再開機能
- **進捗表示**: リアルタイムプログレスバー

### 2. AI自動分類・整理

#### 2.1 写真区分による自動分類
```python
# デジタル写真管理情報基準に準拠した分類
photo_categories = {
    "写真-大分類": ["工事", "測量", "調査", "地質", "広報", "設計", "その他"],
    "写真区分": [
        "着手前及び完成写真",  # 既済部分写真等を含む
        "施工状況写真",
        "安全管理写真",
        "使用材料写真",
        "品質管理写真",
        "出来形管理写真",
        "災害写真",
        "事故写真",
        "その他"  # 公害、環境、補償等
    ],
    "工種": "新土木工事積算体系レベル2準拠",
    "種別": "新土木工事積算体系レベル3準拠",
    "細別": "新土木工事積算体系レベル4準拠"
}
```

#### 2.2 黒板OCR機能（写真管理項目の自動抽出）
- **工事名称**: 工事件名の認識
- **工種情報**: 工種・種別・細別の階層的認識
- **測点情報**: 位置情報・測点番号の抽出
- **撮影日時**: CCYY-MM-DD形式への自動変換
- **寸法情報**: 設計寸法・実測寸法の認識
- **立会者**: 検査立会者名の抽出

#### 2.3 ファイル命名規則の自動適用
```python
# 写真ファイル命名規則（基準準拠）
def generate_photo_filename(serial_number):
    """
    写真ファイル名: Pnnnnnnn.JPG
    P: 固定文字
    nnnnnnn: 7桁の連番（前ゼロ埋めなし）
    """
    return f"P{serial_number:07d}.JPG"

# 参考図ファイル命名規則
def generate_drawing_filename(serial_number, extension):
    """
    参考図ファイル名: Dnnnnnnn.XXX
    D: 固定文字
    nnnnnnn: 7桁の連番
    XXX: 拡張子（JPG, TIF, SVG等）
    """
    return f"D{serial_number:07d}.{extension}"
```

#### 2.4 画質・有効画素数の自動判定
```python
quality_standards = {
    "有効画素数": {
        "最小": 1000000,  # 100万画素
        "推奨": 2000000,  # 200万画素
        "最大": 3000000   # 300万画素
    },
    "解像度の目安": {
        "最小": "1200×900",
        "推奨": "1600×1200",
        "最大": "2000×1500"
    },
    "圧縮設定": "JPEG標準（約1/16圧縮）",
    "編集": "不可（信憑性確保のため）"
}
```

#### 2.5 重複・品質判定
- **類似度判定**: 画像ハッシュによる重複検出（閾値設定可能）
- **黒板文字判読性**: OCR信頼度スコアによる判定
- **撮影対象視認性**: 対象物の明瞭度判定
- **提出頻度写真の識別**: 代表写真フラグの自動設定

### 3. 検索・絞り込み機能

```javascript
// 検索条件の例
const searchParams = {
  location: {
    lat: 35.6762,
    lng: 139.6503,
    radius: 100 // meters
  },
  dateRange: {
    from: "2024-01-01",
    to: "2024-12-31"
  },
  categories: ["土工", "基礎工"],
  keywords: ["配筋", "型枠"],
  quality: "recommended"
}
```

### 4. 位置情報管理

- **地図表示**: Google Maps API統合
- **撮影位置プロット**: GPS情報に基づく自動マッピング
- **エリア検索**: 地図上での範囲選択検索
- **撮影ルート表示**: 時系列での移動経路可視化

### 5. 自動タイトル生成

```
生成例: [工種]_[測点]_[撮影対象]_[撮影日]
→ "基礎工_No.15+20.5_配筋状況_20240315"
```

### 6. 電子納品対応（デジタル写真管理情報基準準拠）

#### 6.1 フォルダ構成の自動生成
```
電子納品ルート/
├── PHOTO/                  # 写真フォルダ（大文字固定）
│   ├── PHOTO.XML           # 写真管理ファイル
│   ├── PHOTO05.DTD         # DTDファイル
│   ├── PHOTO05.XSL         # スタイルシート（任意）
│   ├── PIC/                # 写真ファイル格納フォルダ
│   │   ├── P0000001.JPG    # 写真ファイル（連番）
│   │   ├── P0000002.JPG
│   │   └── ...
│   └── DRA/                # 参考図フォルダ（任意）
│       ├── D0000001.JPG    # 参考図ファイル
│       └── ...
```

#### 6.2 PHOTO.XML自動生成（PHOTO05.DTD準拠）
```xml
<?xml version="1.0" encoding="Shift_JIS"?>
<!DOCTYPE photodata SYSTEM "PHOTO05.DTD">
<?xml-stylesheet type="text/xsl" href="PHOTO05.XSL"?>
<photodata DTD_version="05">
  <基礎情報>
    <写真フォルダ名>PHOTO/PIC</写真フォルダ名>
    <参考図フォルダ名>PHOTO/DRA</参考図フォルダ名>
    <適用要領基準>土木202303-01</適用要領基準>
  </基礎情報>
  <写真情報>
    <写真ファイル情報>
      <シリアル番号>1</シリアル番号>
      <写真ファイル名>P0000001.JPG</写真ファイル名>
      <写真ファイル日本語名>着手前0001.JPG</写真ファイル日本語名>
      <メディア番号>1</メディア番号>
    </写真ファイル情報>
    <撮影工種区分>
      <写真-大分類>工事</写真-大分類>
      <写真区分>着手前及び完成写真</写真区分>
      <工種>舗装修繕工</工種>
      <種別>舗装打換え工</種別>
      <細別>下層路盤</細別>
      <写真タイトル>着手前全景</写真タイトル>
    </撮影工種区分>
    <付加情報>
      <参考図ファイル名>D0000001.JPG</参考図ファイル名>
      <参考図タイトル>平面図</参考図タイトル>
    </付加情報>
    <撮影情報>
      <撮影箇所>測点:1L</撮影箇所>
      <撮影年月日>2024-03-15</撮影年月日>
    </撮影情報>
    <代表写真>1</代表写真>
    <提出頻度写真>1</提出頻度写真>
    <施工管理値>設計寸法400mm・実測寸法405mm</施工管理値>
  </写真情報>
</photodata>
```

#### 6.3 写真管理項目の自動設定ロジック

```python
class PhotoMetadataGenerator:
    """写真管理項目の自動生成クラス"""
    
    # 必須項目（◎）
    REQUIRED_FIELDS = [
        "写真フォルダ名",
        "適用要領基準",
        "シリアル番号",
        "写真ファイル名",
        "メディア番号",
        "写真-大分類",
        "写真タイトル",
        "撮影年月日",
        "代表写真",
        "提出頻度写真"
    ]
    
    # 条件付き必須項目（○）
    CONDITIONAL_FIELDS = {
        "参考図フォルダ名": "参考図が存在する場合",
        "写真区分": "大分類が'工事'の場合",
        "工種": "写真区分が出来形管理写真等の場合",
        "施工管理値": "黒板判読困難な場合"
    }
    
    # 文字数制限
    CHARACTER_LIMITS = {
        "写真フォルダ名": 9,       # 半角英大文字
        "シリアル番号": 7,         # 半角数字
        "写真ファイル名": 12,      # 半角英数大文字
        "写真タイトル": 127,       # 全角文字/半角英数字
        "撮影年月日": 10,          # CCYY-MM-DD形式固定
        "施工管理値": 127          # 全角文字/半角英数字
    }
    
    # 使用可能文字の制限
    CHARSET_RULES = {
        "半角英数大文字": r"^[A-Z0-9_]+$",
        "半角数字": r"^[0-9]+$",
        "全角文字": "JIS X 0208準拠（半角カナ除外）"
    }
```

#### 6.4 工種区分の記入可否判定

| 写真区分 | 工種 | 種別 | 細別 |
|---------|------|------|------|
| 着手前及び完成写真 | × | × | × |
| 施工状況写真 | △ | △ | △ |
| 安全管理写真 | △ | × | × |
| 使用材料写真 | △ | △ | △ |
| 品質管理写真 | ○ | △ | △ |
| 出来形管理写真 | ○ | △ | △ |
| 災害写真 | × | × | × |
| その他 | × | × | × |

（○：記入、△：可能な場合は記入、×：不要）

### 7. 工事写真帳生成

- **テンプレート選択**: 発注者別のレイアウト対応
- **自動レイアウト**: AI による最適配置
- **説明文自動生成**: 黒板情報からの説明文作成
- **出力形式**: PDF, Excel, Word対応

## 📦 出力形式（ベストプラクティス）

### 推奨エクスポート形式

1. **電子納品パッケージ** (.zip)
   - 国土交通省基準準拠
   - PHOTO.XML含む完全パッケージ

2. **工事写真帳** 
   - PDF/A形式（長期保存対応）
   - Excel形式（編集可能）
   - HTML形式（Web閲覧用）

3. **データ連携**
   - JSON形式（API連携用）
   - CSV形式（表計算ソフト用）

4. **バックアップ**
   - 増分バックアップ（差分のみ）
   - フルバックアップ（全データ）

## 🔌 外部連携

### 施工管理ソフトウェア連携API

#### RESTful API エンドポイント

```javascript
// 写真アップロードAPI
POST /api/v1/photos/upload
Content-Type: multipart/form-data
{
  "project_id": "PRJ-2024-001",
  "photos": [binary],
  "metadata": {
    "contractor": "○○建設",
    "location": "測点No.15",
    "date": "2024-03-15"
  }
}

// 写真検索API
GET /api/v1/photos/search
Parameters:
  - project_id: string
  - date_from: YYYY-MM-DD
  - date_to: YYYY-MM-DD
  - category: string (写真区分)
  - keyword: string
  - location: {lat, lng, radius}

// PHOTO.XML生成API
POST /api/v1/export/photo-xml
{
  "project_id": "PRJ-2024-001",
  "photo_ids": [1, 2, 3...],
  "dtd_version": "05",
  "encoding": "Shift_JIS"
}

// Webhook通知設定
POST /api/v1/webhooks
{
  "event_type": "photo_processed",
  "callback_url": "https://your-system.com/webhook",
  "secret": "your-secret-key"
}
```

#### 親会社システムとの連携仕様

```python
class ParentSystemIntegration:
    """親会社の施工管理ソフトウェアとの連携"""
    
    # 認証方式
    AUTH_METHOD = "OAuth2.0"
    
    # データ同期
    SYNC_INTERVAL = 300  # 5分ごと
    
    # 連携可能データ
    SYNC_DATA = {
        "projects": "工事案件情報",
        "contractors": "施工業者情報",
        "schedules": "工程表データ",
        "drawings": "設計図面データ",
        "specifications": "仕様書データ"
    }
    
    def import_project_data(self, project_id):
        """プロジェクトデータのインポート"""
        # 工事概要の取得
        # 工種マスタの取得
        # 施工業者情報の取得
        pass
    
    def export_photo_data(self, project_id, photos):
        """写真データのエクスポート"""
        # 写真メタデータの送信
        # サムネイルの生成・送信
        # 処理状態の通知
        pass
```

#### データ形式とスキーマ

```typescript
// TypeScript型定義
interface PhotoMetadata {
  id: string;
  fileName: string;
  serialNumber: number;
  category: PhotoCategory;
  construction: {
    majorCategory: "工事" | "測量" | "調査" | "地質" | "広報" | "設計" | "その他";
    photoType: PhotoType;
    workType?: string;  // 工種
    workKind?: string;  // 種別
    workDetail?: string; // 細別
  };
  location: {
    point: string;      // 測点
    latitude?: number;
    longitude?: number;
  };
  shootingDate: string; // CCYY-MM-DD
  blackboard?: {
    text: string;
    ocrConfidence: number;
  };
  quality: {
    pixels: number;
    fileSize: number;
    isRepresentative: boolean;  // 代表写真
    submissionFrequency: boolean; // 提出頻度写真
  };
}
```

## 🔧 技術スタック

### フロントエンド
- **フレームワーク**: Next.js 14+ (App Router)
- **言語**: TypeScript
- **UI**: Material-UI / Tailwind CSS
- **状態管理**: Redux Toolkit / Zustand
- **地図**: Google Maps API / Mapbox

### バックエンド
- **API**: Node.js + Express / FastAPI (Python)
- **AI/ML**: 
  - Amazon Rekognition（画像認識）
  - Amazon Textract（OCR）
  - TensorFlow / PyTorch（カスタムモデル）
- **データベース**: PostgreSQL + Redis
- **検索エンジン**: Elasticsearch

### インフラ (AWS)
- **コンピュート**: Lambda, ECS/Fargate
- **ストレージ**: S3, EFS
- **データベース**: RDS (PostgreSQL), DynamoDB
- **AI/ML**: SageMaker, Rekognition, Textract
- **その他**: CloudFront, API Gateway, SQS, EventBridge

## 📈 性能目標

| 指標 | 目標値 | 備考 |
|------|--------|------|
| 同時アップロード | 10,000枚 | 並列処理により実現 |
| 1枚あたり処理時間 | <2秒 | AI分類含む |
| 検索レスポンス | <500ms | インデックス検索 |
| 総容量上限 | 無制限 | S3スケーラビリティ |
| 同時接続ユーザー | 1,000人 | オートスケーリング対応 |
| 可用性 | 99.9% | SLA保証 |

## 🚦 開発ロードマップ

### Phase 1: MVP (3ヶ月)
- ✅ 基本的な写真アップロード機能
- ✅ 黒板OCRによる自動分類
- ✅ 基本的な検索機能
- ✅ 写真一覧表示

### Phase 2: AI強化 (3ヶ月)
- ⏳ 高度な画像認識による分類
- ⏳ 重複検出・品質判定
- ⏳ 自動タイトル生成
- ⏳ 位置情報管理

### Phase 3: 電子納品対応 (2ヶ月)
- ⏳ PHOTO.XML自動生成
- ⏳ 工事写真帳作成機能
- ⏳ 各種エクスポート機能

### Phase 4: 連携・拡張 (2ヶ月)
- ⏳ 施工管理ソフト連携API
- ⏳ 高度な分析機能
- ⏳ モバイルアプリ対応

## ❓ FAQ（よくある質問）

### Q1: 写真の編集は可能ですか？
**A:** いいえ。デジタル写真管理情報基準により、写真の信憑性確保のため編集は認められていません。明るさ調整、トリミング、回転等も不可です。

### Q2: 対応している画像形式は？
**A:** 基準に準拠し、以下の形式に対応しています：
- 写真ファイル：JPEG、TIFF、SVG（監督職員承諾が必要）
- 参考図ファイル：JPEG、TIFF、SVG
- 圧縮設定：JPEG標準（約1/16圧縮）

### Q3: ファイル名は自由に付けられますか？
**A:** いいえ。以下の命名規則に従う必要があります：
- 写真：Pnnnnnnn.JPG（例：P0000001.JPG）
- 参考図：Dnnnnnnn.XXX（例：D0000001.JPG）

### Q4: 写真の最適な画素数は？
**A:** 200万画素程度（1600×1200）が推奨です。最小100万画素、最大300万画素の範囲内で、黒板の文字が判読できることが条件です。

### Q5: 手書き黒板の認識精度は？
**A:** OCR技術により約85-90%の精度で認識可能です。認識できない場合は手動修正機能があります。

### Q6: オンプレミス版はありますか？
**A:** 現在はクラウド版のみですが、セキュリティ要件に応じてVPC内での構築やオンプレミス版の開発も検討可能です。

### Q7: 既存の写真管理システムからの移行は可能ですか？
**A:** はい。CSV、Excel形式でのメタデータインポート、既存フォルダ構造の維持インポートに対応しています。

### Q8: 写真の保管期限は？
**A:** システム上の制限はありません。契約プランにより保管容量が異なります。工事完成後5年以上の保管を推奨します。

### Q9: 同時に何人まで使用できますか？
**A:** 基本プランで100人、エンタープライズプランで1,000人まで同時接続可能です。自動スケーリングにより増設も可能です。

### Q10: APIの利用制限は？
**A:** 以下の制限があります：
- アップロード：100GB/日
- API呼び出し：10,000回/時間
- 同時処理：100件
※エンタープライズプランでは制限緩和可能

## 🔍 データバリデーション機能

### 写真ファイルの検証

```python
class PhotoValidator:
    """デジタル写真管理情報基準に基づくバリデーション"""
    
    def validate_photo(self, photo_file):
        validations = {
            "file_format": self._check_format,         # JPEG/TIFF/SVG
            "file_naming": self._check_naming,         # Pnnnnnnn.JPG
            "pixel_count": self._check_pixels,         # 100-300万画素
            "file_size": self._check_size,            # 適切なサイズ
            "exif_data": self._check_exif,            # EXIF情報
            "edited": self._check_unedited,           # 編集の痕跡
            "blackboard": self._check_blackboard_text  # 黒板文字判読性
        }
        
    def _check_pixels(self, image):
        """有効画素数のチェック"""
        width, height = image.size
        pixel_count = width * height
        
        if pixel_count < 1_000_000:
            return "NG: 画素数不足（100万画素未満）"
        elif pixel_count > 3_000_000:
            return "警告: 画素数過大（300万画素超）"
        else:
            return "OK"
    
    def _check_unedited(self, photo_file):
        """写真編集の検出"""
        # EXIF情報の整合性チェック
        # ファイルハッシュの検証
        # 編集ソフトウェアの痕跡検出
        return "写真の信憑性検証"
```

### XML管理ファイルの検証

```python
class XMLValidator:
    """PHOTO05.DTD準拠のXML検証"""
    
    def validate_xml(self, xml_content):
        # DTDに対する妥当性検証
        # 必須項目の存在チェック
        # 文字数制限の確認
        # 使用文字の適合性確認
        # 日付形式（CCYY-MM-DD）の検証
        # 参照整合性（写真ファイルの存在確認）
        pass
    
    def check_required_fields(self, photo_info):
        """必須項目のチェック"""
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in photo_info or not photo_info[field]:
                missing_fields.append(field)
        return missing_fields
    
    def check_character_limits(self, photo_info):
        """文字数制限のチェック"""
        violations = []
        for field, limit in self.CHARACTER_LIMITS.items():
            if field in photo_info and len(photo_info[field]) > limit:
                violations.append(f"{field}: {len(photo_info[field])}文字（上限{limit}文字）")
        return violations
```

### エラー処理とレポート機能

```python
class ValidationReport:
    """検証レポートの生成"""
    
    def generate_report(self, validation_results):
        report = {
            "total_photos": 0,
            "valid_photos": 0,
            "invalid_photos": 0,
            "warnings": [],
            "errors": [],
            "statistics": {
                "average_file_size": 0,
                "average_pixels": 0,
                "blackboard_readable_rate": 0
            }
        }
        return report
```

## 🛡️ セキュリティ

- **認証**: AWS Cognito / Auth0
- **暗号化**: 保存時・転送時の暗号化
- **アクセス制御**: RBAC（ロールベース）
- **監査ログ**: 全操作の記録
- **データ保護**: GDPR/個人情報保護法準拠

## 💻 開発者向け実装ガイド

### セットアップ手順

```bash
# リポジトリのクローン
git clone https://github.com/construction-bpo/photo-management.git
cd photo-management

# 環境変数の設定
cp .env.example .env
# AWS認証情報、API キー等を設定

# Dockerコンテナの起動
docker-compose up -d

# データベースマイグレーション
npm run db:migrate

# 開発サーバーの起動
npm run dev
```

### ディレクトリ構造

```
photo-management/
├── frontend/               # Next.js フロントエンド
│   ├── components/        # UIコンポーネント
│   ├── features/          # 機能別モジュール
│   │   ├── upload/       # アップロード機能
│   │   ├── ai-process/   # AI処理機能
│   │   ├── search/       # 検索機能
│   │   └── export/       # エクスポート機能
│   └── utils/            # ユーティリティ
├── backend/               # Node.js/Python バックエンド
│   ├── api/              # APIエンドポイント
│   ├── services/         # ビジネスロジック
│   │   ├── ocr/         # OCRサービス
│   │   ├── image-ai/    # 画像認識AI
│   │   └── xml-generator/ # XML生成
│   ├── models/           # データモデル
│   └── validators/       # バリデーション
├── ai-models/            # AI/MLモデル
│   ├── classification/   # 分類モデル
│   ├── ocr/             # OCRモデル
│   └── quality/         # 品質判定モデル
├── infrastructure/       # IaCコード
│   ├── terraform/       # Terraformファイル
│   └── kubernetes/      # K8s設定
└── docs/                # ドキュメント
    ├── api/            # API仕様書
    └── standards/      # 基準書
```

### テスト戦略

```javascript
// ユニットテスト例（Jest）
describe('PhotoValidator', () => {
  test('ファイル名規則の検証', () => {
    const validator = new PhotoValidator();
    expect(validator.validateFileName('P0000001.JPG')).toBe(true);
    expect(validator.validateFileName('photo001.jpg')).toBe(false);
  });
  
  test('画素数の検証', () => {
    const validator = new PhotoValidator();
    const result = validator.validatePixels(1600, 1200);
    expect(result.isValid).toBe(true);
    expect(result.pixelCount).toBe(1920000);
  });
});

// E2Eテスト例（Playwright）
test('写真アップロードから電子納品まで', async ({ page }) => {
  await page.goto('/upload');
  await page.setInputFiles('#photo-input', 'test-photos/*.jpg');
  await page.click('#process-button');
  await page.waitForSelector('.process-complete');
  await page.click('#export-xml');
  const download = await page.waitForEvent('download');
  expect(download.suggestedFilename()).toBe('PHOTO.XML');
});
```

### デプロイメント

```yaml
# GitHub Actions CI/CD
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and test
        run: |
          npm install
          npm test
          npm run build
      - name: Deploy to AWS
        run: |
          aws s3 sync ./build s3://${{ secrets.S3_BUCKET }}
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CF_DIST_ID }}
```

### 監視とログ

```python
# ログ設定例
import logging
from aws_lambda_powertools import Logger

logger = Logger(service="photo-management")

@logger.inject_lambda_context
def process_photo_handler(event, context):
    logger.info("写真処理開始", extra={
        "photo_count": len(event['photos']),
        "project_id": event['project_id']
    })
    
    # CloudWatch メトリクス
    cloudwatch.put_metric_data(
        Namespace='PhotoManagement',
        MetricData=[
            {
                'MetricName': 'ProcessedPhotos',
                'Value': photo_count,
                'Unit': 'Count'
            }
        ]
    )
```

## 📝 ライセンス

Proprietary - 建設BPO事業会社

## 🤝 お問い合わせ

株式会社ウィズテック
Email: yo-sekino@wiz-tech.jp

---

*このシステムは、建設業界のDX推進と働き方改革に貢献することを目指しています。*
