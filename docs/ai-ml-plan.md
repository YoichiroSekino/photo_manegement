# AI/ML開発計画書

**バージョン**: 1.0
**作成日**: 2025-11-02
**対象システム**: 工事写真自動整理システム

---

## 目次

1. [AI/ML機能概要](#1-aiml機能概要)
2. [OCR実装計画](#2-ocr実装計画)
3. [画像分類モデル開発](#3-画像分類モデル開発)
4. [品質評価モデル開発](#4-品質評価モデル開発)
5. [重複検出アルゴリズム](#5-重複検出アルゴリズム)
6. [学習データ準備計画](#6-学習データ準備計画)
7. [モデル評価・改善計画](#7-モデル評価改善計画)
8. [推論パフォーマンス最適化](#8-推論パフォーマンス最適化)

---

## 1. AI/ML機能概要

### 1.1 AI機能マップ

| 機能 | 技術 | 精度目標 | 優先度 |
|------|------|---------|-------|
| **黒板OCR** | Amazon Textract | 85%以上 | 高 |
| **工種分類** | Rekognition Custom Labels | 80%以上 | 高 |
| **写真区分判定** | カスタムCNNモデル | 75%以上 | 中 |
| **品質評価** | カスタム回帰モデル | 相関0.7以上 | 中 |
| **重複検出** | Perceptual Hash | 偽陽性5%以下 | 低 |
| **タイトル生成** | ルールベース + NLP | - | 低 |

### 1.2 AI処理フロー

```
写真アップロード
    │
    ▼
┌──────────────────┐
│ 前処理           │
│ - リサイズ       │
│ - 正規化         │
└────────┬─────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│ OCR処理          │              │ 画像分類         │
│ (Textract)       │              │ (Rekognition)    │
│                  │              │                  │
│ 出力:             │              │ 出力:             │
│ - 工事名         │              │ - 工種            │
│ - 測点           │              │ - 写真区分        │
│ - 撮影日         │              │ - 信頼度          │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         │                                 │
         ▼                                 ▼
┌──────────────────────────────────────────────────┐
│              メタデータ統合                        │
│              - OCR + 分類結果マージ                │
│              - 矛盾チェック                        │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ 品質評価         │
│ (カスタムモデル)  │
│                  │
│ 出力:             │
│ - 総合スコア      │
│ - 推奨アクション  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DB保存           │
└──────────────────┘
```

---

## 2. OCR実装計画

### 2.1 Amazon Textract採用戦略

#### 採用理由

1. **高精度**: 手書き文字対応、日本語精度85-90%
2. **マネージド**: インフラ管理不要
3. **スケーラビリティ**: 自動スケール
4. **コスト**: $1.50/1,000ページ（detect_document_text）

#### 実装アプローチ

```python
# services/ocr_service.py
import boto3
from typing import Dict, List, Optional
import re
from datetime import datetime

class TextractOCRService:
    """黒板OCR処理サービス"""

    def __init__(self):
        self.textract = boto3.client('textract', region_name='ap-northeast-1')

    def process_blackboard(
        self,
        s3_bucket: str,
        s3_key: str,
        confidence_threshold: float = 80.0
    ) -> Dict:
        """
        黒板画像からテキスト抽出

        Returns:
            {
                'raw_text': str,
                'structured_data': {
                    '工事名': str,
                    '工種': str,
                    '測点': str,
                    '撮影日': str,
                    '立会者': str,
                    '寸法': {'設計': int, '実測': int}
                },
                'confidence': float,
                'processing_time': float
            }
        """
        start_time = time.time()

        # Textract実行
        response = self.textract.detect_document_text(
            Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
        )

        # テキスト抽出
        lines = self._extract_lines(response, confidence_threshold)
        raw_text = '\n'.join([line['text'] for line in lines])

        # 構造化データ抽出
        structured_data = self._parse_construction_blackboard(lines)

        # 平均信頼度計算
        avg_confidence = sum(line['confidence'] for line in lines) / len(lines) if lines else 0

        return {
            'raw_text': raw_text,
            'structured_data': structured_data,
            'confidence': round(avg_confidence, 2),
            'processing_time': time.time() - start_time,
            'line_count': len(lines)
        }

    def _extract_lines(
        self,
        response: Dict,
        confidence_threshold: float
    ) -> List[Dict]:
        """Textractレスポンスから行単位でテキスト抽出"""
        lines = []

        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                confidence = block['Confidence']

                if confidence >= confidence_threshold:
                    lines.append({
                        'text': block['Text'],
                        'confidence': confidence,
                        'geometry': block['Geometry']
                    })

        return lines

    def _parse_construction_blackboard(self, lines: List[Dict]) -> Dict:
        """
        建設黒板特有の情報を抽出

        一般的な黒板レイアウト:
        ┌────────────────────────┐
        │ 工事名: ○○道路改良工事   │
        │ 工種: 基礎工             │
        │ 測点: No.15+20.5        │
        │ 撮影日: 2024/03/15      │
        │ 立会者: ○○建設 山田太郎  │
        │ 設計寸法: 400mm          │
        │ 実測寸法: 405mm          │
        └────────────────────────┘
        """
        metadata = {
            '工事名': None,
            '工種': None,
            '測点': None,
            '撮影日': None,
            '立会者': None,
            '寸法': {}
        }

        for line in lines:
            text = line['text']

            # 工事名抽出
            if '工事' in text and not metadata['工事名']:
                metadata['工事名'] = self._extract_project_name(text)

            # 工種抽出
            elif '工種' in text or '種別' in text:
                metadata['工種'] = self._extract_work_type(text)

            # 測点抽出
            elif '測点' in text or 'No.' in text or 'NO.' in text:
                metadata['測点'] = self._extract_station_number(text)

            # 撮影日抽出
            elif '撮影' in text or '年月日' in text:
                metadata['撮影日'] = self._extract_date(text)

            # 立会者抽出
            elif '立会' in text or '立ち会い' in text:
                metadata['立会者'] = self._extract_witness(text)

            # 寸法抽出
            elif '設計' in text or '実測' in text or '寸法' in text:
                dimensions = self._extract_dimensions(text)
                metadata['寸法'].update(dimensions)

        return metadata

    def _extract_project_name(self, text: str) -> Optional[str]:
        """工事名抽出"""
        # パターン: "工事名: ○○道路改良工事" or "○○道路改良工事"
        patterns = [
            r'工事名[：:]\s*(.+)',
            r'件名[：:]\s*(.+)',
            r'(.+工事)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_work_type(self, text: str) -> Optional[str]:
        """工種抽出"""
        # パターン: "工種: 基礎工"
        patterns = [
            r'工種[：:]\s*(.+)',
            r'種別[：:]\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_station_number(self, text: str) -> Optional[str]:
        """測点番号抽出"""
        # パターン: "No.15+20.5" or "測点: 1L" or "No.123"
        patterns = [
            r'No\.?\s*(\d+[\+\-]?\d*\.?\d*[A-Z]?)',
            r'NO\.?\s*(\d+[\+\-]?\d*\.?\d*[A-Z]?)',
            r'測点[：:]\s*(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"No.{match.group(1)}"

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """撮影日抽出（CCYY-MM-DD形式に変換）"""
        # パターン:
        # - 2024/03/15
        # - 2024-03-15
        # - R6.3.15 (令和6年)
        # - H30.12.25 (平成30年)

        # 西暦パターン
        western_patterns = [
            r'(\d{4})[\-/年](\d{1,2})[\-/月](\d{1,2})',
        ]

        for pattern in western_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.groups()
                return f"{year}-{int(month):02d}-{int(day):02d}"

        # 和暦パターン
        jp_match = re.search(r'([RrHhSs])(\d{1,2})[\.\-/年](\d{1,2})[\.\-/月](\d{1,2})', text)
        if jp_match:
            era, year_jp, month, day = jp_match.groups()
            year_western = self._convert_japanese_year(era.upper(), int(year_jp))
            if year_western:
                return f"{year_western}-{int(month):02d}-{int(day):02d}"

        return None

    def _convert_japanese_year(self, era: str, year: int) -> Optional[int]:
        """和暦を西暦に変換"""
        era_base_years = {
            'R': 2018,  # 令和
            'H': 1988,  # 平成
            'S': 1925,  # 昭和
        }

        if era in era_base_years:
            return era_base_years[era] + year

        return None

    def _extract_witness(self, text: str) -> Optional[str]:
        """立会者抽出"""
        # パターン: "立会者: ○○建設 山田太郎"
        patterns = [
            r'立会[者]?[：:]\s*(.+)',
            r'立ち会い[：:]\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_dimensions(self, text: str) -> Dict[str, int]:
        """寸法情報抽出"""
        dimensions = {}

        # 設計寸法
        design_patterns = [
            r'設計[寸法]?[：:]\s*(\d+)\s*mm',
            r'設計[：:]\s*(\d+)',
        ]

        for pattern in design_patterns:
            match = re.search(pattern, text)
            if match:
                dimensions['設計'] = int(match.group(1))
                break

        # 実測寸法
        actual_patterns = [
            r'実測[寸法]?[：:]\s*(\d+)\s*mm',
            r'実測[：:]\s*(\d+)',
        ]

        for pattern in actual_patterns:
            match = re.search(pattern, text)
            if match:
                dimensions['実測'] = int(match.group(1))
                break

        return dimensions
```

### 2.2 OCR精度向上施策

#### Phase 1: 前処理最適化（Month 2-3）

```python
# services/image_preprocessing.py
import cv2
import numpy as np
from PIL import Image

class BlackboardPreprocessor:
    """黒板画像の前処理"""

    def enhance_for_ocr(self, image_path: str) -> str:
        """OCR精度向上のための画像前処理"""

        # 画像読み込み
        img = cv2.imread(image_path)

        # 1. グレースケール変換
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 3. コントラスト強調（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. 二値化（適応的閾値処理）
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # 5. モルフォロジー変換（小さなノイズ除去）
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # 処理済み画像を保存
        output_path = image_path.replace('.jpg', '_preprocessed.jpg')
        cv2.imwrite(output_path, cleaned)

        return output_path
```

#### Phase 2: カスタム辞書（Month 4-5）

```python
# 建設業界特有の用語辞書
CONSTRUCTION_VOCABULARY = {
    # 工種
    '土工', '基礎工', '躯体工', '舗装工', '排水工',
    '擁壁工', 'コンクリート工', '鋼橋工',

    # 測点表記
    'No.', 'STA.', '測点',

    # 寸法
    '設計寸法', '実測寸法', 'mm', 'cm', 'm',

    # その他
    '立会者', '工事名', '撮影日', '施工者',
}

# Textract後の補正処理
def post_process_ocr(raw_text: str) -> str:
    """OCR結果の補正"""

    # よくある誤認識パターンの修正
    corrections = {
        'No．': 'No.',
        'N0.': 'No.',
        '測占': '測点',
        '工稿': '工種',
        # ... 他の誤認識パターン
    }

    corrected_text = raw_text
    for wrong, correct in corrections.items():
        corrected_text = corrected_text.replace(wrong, correct)

    return corrected_text
```

#### Phase 3: 精度モニタリング（Month 6以降）

```python
# monitoring/ocr_accuracy.py
class OCRAccuracyMonitor:
    """OCR精度監視"""

    def track_accuracy(self, photo_id: str, ocr_result: Dict, manual_correction: Dict):
        """手動修正データから精度を計測"""

        metrics = {
            'photo_id': photo_id,
            'timestamp': datetime.utcnow(),
            'fields_detected': len([v for v in ocr_result['structured_data'].values() if v]),
            'fields_correct': 0,
            'character_accuracy': 0.0,
        }

        # フィールド単位の正解率
        for field, ocr_value in ocr_result['structured_data'].items():
            manual_value = manual_correction.get(field)
            if ocr_value == manual_value:
                metrics['fields_correct'] += 1

        # 文字単位の正解率（Levenshtein距離）
        ocr_text = ocr_result['raw_text']
        manual_text = manual_correction.get('full_text', '')

        if manual_text:
            from Levenshtein import distance
            max_len = max(len(ocr_text), len(manual_text))
            metrics['character_accuracy'] = 1 - (distance(ocr_text, manual_text) / max_len)

        # CloudWatch Metricsに送信
        self._send_to_cloudwatch(metrics)

        return metrics
```

---

## 3. 画像分類モデル開発

### 3.1 Amazon Rekognition Custom Labels

#### 学習データ要件

| カテゴリ | 最小枚数 | 推奨枚数 | 説明 |
|---------|---------|---------|------|
| **着手前及び完成写真** | 50 | 200+ | 工事開始前・完了後の全景写真 |
| **施工状況写真** | 100 | 500+ | 作業中の写真（最も多様） |
| **安全管理写真** | 50 | 150+ | 安全設備、標識等 |
| **使用材料写真** | 50 | 150+ | 材料検収写真 |
| **品質管理写真** | 80 | 300+ | 試験、検査写真 |
| **出来形管理写真** | 80 | 300+ | 完成部分の寸法確認写真 |
| **その他** | 30 | 100+ | 上記以外 |

#### モデル学習手順

```bash
# 1. S3にトレーニングデータアップロード
aws s3 sync ./training_data s3://construction-photos-training/

# 2. マニフェストファイル作成
python scripts/create_manifest.py \
  --input-dir ./training_data \
  --output s3://construction-photos-training/manifest.json

# 3. Rekognition プロジェクト作成
aws rekognition create-project \
  --project-name construction-photo-classifier

# 4. データセット作成
aws rekognition create-dataset \
  --project-arn arn:aws:rekognition:ap-northeast-1:ACCOUNT_ID:project/construction-photo-classifier \
  --dataset-type TRAIN \
  --dataset-source '{"GroundTruthManifest": {"S3Object": {"Bucket": "construction-photos-training", "Name": "manifest.json"}}}'

# 5. モデル学習開始
aws rekognition create-project-version \
  --project-arn arn:aws:rekognition:ap-northeast-1:ACCOUNT_ID:project/construction-photo-classifier \
  --version-name version-1 \
  --output-config '{"S3Bucket": "construction-photos-training", "S3KeyPrefix": "output/"}'

# 学習完了まで約2-24時間

# 6. モデルデプロイ
aws rekognition start-project-version \
  --project-version-arn arn:aws:rekognition:ap-northeast-1:ACCOUNT_ID:project/construction-photo-classifier/version/version-1/... \
  --min-inference-units 1
```

### 3.2 カスタムCNNモデル（オプション）

より高精度が必要な場合のカスタムモデル実装：

```python
# ai-models/classification/custom_classifier.py
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

class ConstructionPhotoClassifier:
    """工事写真分類カスタムモデル"""

    CATEGORIES = [
        "着手前及び完成写真",
        "施工状況写真",
        "安全管理写真",
        "使用材料写真",
        "品質管理写真",
        "出来形管理写真",
        "災害写真",
        "その他"
    ]

    def __init__(self):
        self.model = self._build_model()

    def _build_model(self):
        """モデル構築（EfficientNetB0ベース）"""

        base_model = keras.applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )

        # Feature extractionフェーズでは基底モデルをフリーズ
        base_model.trainable = False

        # カスタム分類ヘッド
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(len(self.CATEGORIES), activation='softmax')
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3)]
        )

        return model

    def train(
        self,
        train_data_dir: str,
        val_data_dir: str,
        epochs: int = 30,
        batch_size: int = 32
    ):
        """モデル学習"""

        # データ拡張
        train_datagen = keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        val_datagen = keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255
        )

        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='categorical',
            classes=self.CATEGORIES
        )

        val_generator = val_datagen.flow_from_directory(
            val_data_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='categorical',
            classes=self.CATEGORIES
        )

        # コールバック
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                'models/best_classifier.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7
            )
        ]

        # Phase 1: Feature extraction
        history_1 = self.model.fit(
            train_generator,
            epochs=15,
            validation_data=val_generator,
            callbacks=callbacks
        )

        # Phase 2: Fine-tuning
        # 基底モデルの上位層をアンフリーズ
        self.model.layers[0].trainable = True
        for layer in self.model.layers[0].layers[:100]:
            layer.trainable = False

        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-5),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3)]
        )

        history_2 = self.model.fit(
            train_generator,
            epochs=epochs,
            initial_epoch=15,
            validation_data=val_generator,
            callbacks=callbacks
        )

        return history_1, history_2

    def predict(self, image_path: str) -> Dict:
        """推論"""

        img = keras.preprocessing.image.load_img(
            image_path,
            target_size=(224, 224)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, 0) / 255.0

        predictions = self.model.predict(img_array)[0]

        results = []
        for i, category in enumerate(self.CATEGORIES):
            results.append({
                'category': category,
                'confidence': float(predictions[i])
            })

        results.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            'primary_category': results[0]['category'],
            'confidence': results[0]['confidence'],
            'top_3_predictions': results[:3]
        }
```

---

## 4. 品質評価モデル開発

### 4.1 評価指標定義

```python
# domain/models/quality_metrics.py
from dataclasses import dataclass

@dataclass
class PhotoQualityMetrics:
    """写真品質評価指標"""

    # 技術的品質（客観的）
    pixel_count: int              # 有効画素数
    sharpness_score: float        # シャープネス（0-100）
    brightness_score: float       # 明るさ（0-100）
    contrast_score: float         # コントラスト（0-100）
    noise_level: float            # ノイズレベル（0-100、低い方が良い）

    # 内容品質（主観的）
    blackboard_readable: bool     # 黒板判読可否
    subject_clarity: float        # 撮影対象の明瞭度（0-100）
    composition_score: float      # 構図スコア（0-100）

    # 準拠性
    compliant_with_standards: bool  # 基準準拠
    file_name_valid: bool          # ファイル名規則
    metadata_complete: bool        # メタデータ完全性

    # 総合評価
    overall_score: float          # 総合スコア（0-100）
    recommendation: str           # 推奨アクション

    def calculate_overall_score(self) -> float:
        """総合スコア計算"""

        # 重み付け
        weights = {
            'technical': 0.3,    # 技術的品質
            'content': 0.4,      # 内容品質
            'compliance': 0.3    # 準拠性
        }

        # 技術的品質スコア
        technical_score = (
            self.sharpness_score * 0.4 +
            self.brightness_score * 0.3 +
            self.contrast_score * 0.2 +
            (100 - self.noise_level) * 0.1
        )

        # 内容品質スコア
        content_score = (
            (100 if self.blackboard_readable else 0) * 0.5 +
            self.subject_clarity * 0.3 +
            self.composition_score * 0.2
        )

        # 準拠性スコア
        compliance_score = (
            (100 if self.compliant_with_standards else 0) * 0.4 +
            (100 if self.file_name_valid else 0) * 0.3 +
            (100 if self.metadata_complete else 0) * 0.3
        )

        # 総合スコア
        overall = (
            technical_score * weights['technical'] +
            content_score * weights['content'] +
            compliance_score * weights['compliance']
        )

        return round(overall, 2)

    def get_recommendation(self) -> str:
        """推奨アクション判定"""
        score = self.calculate_overall_score()

        if score >= 80:
            return "提出に最適"
        elif score >= 65:
            return "提出可能"
        elif score >= 50:
            return "要確認・改善推奨"
        else:
            return "再撮影を強く推奨"
```

### 4.2 品質評価実装

```python
# services/quality_assessment_service.py
import cv2
import numpy as np
from PIL import Image
from typing import Dict

class QualityAssessmentService:
    """写真品質評価サービス"""

    def assess_photo(self, image_path: str) -> PhotoQualityMetrics:
        """総合品質評価"""

        # 画像読み込み
        img_pil = Image.open(image_path)
        img_cv = cv2.imread(image_path)

        # 各種指標計算
        metrics = PhotoQualityMetrics(
            pixel_count=self._calculate_pixel_count(img_pil),
            sharpness_score=self._calculate_sharpness(img_cv),
            brightness_score=self._calculate_brightness(img_cv),
            contrast_score=self._calculate_contrast(img_cv),
            noise_level=self._calculate_noise(img_cv),
            blackboard_readable=self._check_blackboard_readability(img_cv),
            subject_clarity=self._assess_subject_clarity(img_cv),
            composition_score=self._assess_composition(img_cv),
            compliant_with_standards=self._check_compliance(img_pil),
            file_name_valid=self._validate_filename(image_path),
            metadata_complete=True,  # 別途チェック
            overall_score=0.0,
            recommendation=""
        )

        # 総合スコア計算
        metrics.overall_score = metrics.calculate_overall_score()
        metrics.recommendation = metrics.get_recommendation()

        return metrics

    def _calculate_sharpness(self, img: np.ndarray) -> float:
        """シャープネス計算（Laplacian分散法）"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        # 0-100スケールに正規化
        # 経験的に、variance > 100で鮮明、< 50でぼやけている
        score = min(100, (variance / 100) * 100)

        return round(score, 2)

    def _calculate_brightness(self, img: np.ndarray) -> float:
        """明るさ評価"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = hsv[:, :, 2].mean()

        # 最適範囲: 100-180 (0-255スケール)
        if 100 <= brightness <= 180:
            score = 100
        elif brightness < 100:
            score = (brightness / 100) * 100
        else:  # brightness > 180
            score = ((255 - brightness) / 75) * 100

        return round(max(0, score), 2)

    def _calculate_contrast(self, img: np.ndarray) -> float:
        """コントラスト評価（標準偏差法）"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        std_dev = np.std(gray)

        # 標準偏差が高い = コントラストが高い
        # 経験的に、std > 50で良好
        score = min(100, (std_dev / 50) * 100)

        return round(score, 2)

    def _calculate_noise(self, img: np.ndarray) -> float:
        """ノイズレベル推定"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ノイズ推定（高周波成分の分散）
        h, w = gray.shape
        roi_size = min(h, w) // 4

        # 画像中心部のROI
        center_roi = gray[
            h//2 - roi_size//2 : h//2 + roi_size//2,
            w//2 - roi_size//2 : w//2 + roi_size//2
        ]

        # ハイパスフィルタ
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        filtered = cv2.filter2D(center_roi, -1, kernel)
        noise = np.std(filtered)

        # 0-100スケール（低い方が良い）
        noise_score = min(100, (noise / 20) * 100)

        return round(noise_score, 2)

    def _check_blackboard_readability(self, img: np.ndarray) -> bool:
        """黒板判読性チェック（簡易版）"""

        # エッジ検出で文字の有無を判定
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size

        # エッジ密度が一定以上なら文字ありと判定
        return edge_density > 0.05

    def _assess_subject_clarity(self, img: np.ndarray) -> float:
        """撮影対象の明瞭度評価"""

        # 簡易版: 画像中央部のシャープネス
        h, w = img.shape[:2]
        center_region = img[h//4:3*h//4, w//4:3*w//4]

        gray = cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        score = min(100, (variance / 100) * 100)
        return round(score, 2)

    def _assess_composition(self, img: np.ndarray) -> float:
        """構図評価（Rule of Thirds）"""

        # 簡易版: 画像の重心が中央付近にあるかチェック
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        moments = cv2.moments(binary)
        if moments['m00'] == 0:
            return 50.0  # デフォルト

        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])

        h, w = img.shape[:2]
        center_x, center_y = w // 2, h // 2

        # 重心と中心の距離
        distance = np.sqrt((cx - center_x)**2 + (cy - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)

        # 距離が近いほど高スコア
        score = (1 - distance / max_distance) * 100

        return round(score, 2)

    def _check_compliance(self, img: Image.Image) -> bool:
        """基準準拠チェック"""

        width, height = img.size
        pixel_count = width * height

        # 有効画素数チェック（100万〜300万）
        return 1_000_000 <= pixel_count <= 3_000_000

    def _validate_filename(self, file_path: str) -> bool:
        """ファイル名規則チェック"""
        import re
        from pathlib import Path

        filename = Path(file_path).name

        # Pnnnnnnn.JPG 形式
        pattern = r'^P\d{7}\.JPG$'
        return bool(re.match(pattern, filename))
```

---

## 5. 重複検出アルゴリズム

### 5.1 パーセプチュアルハッシュ実装

```python
# services/duplicate_detection_service.py
import imagehash
from PIL import Image
from typing import List, Tuple, Dict

class DuplicateDetectionService:
    """重複写真検出サービス"""

    def __init__(self, threshold: int = 5):
        """
        Args:
            threshold: ハミング距離の閾値（0-64）
                      5以下: ほぼ同一
                      10以下: 非常に似ている
                      15以下: 似ている
        """
        self.threshold = threshold

    def calculate_hash(self, image_path: str) -> str:
        """パーセプチュアルハッシュ計算"""
        try:
            img = Image.open(image_path)
            # pHash (perceptual hash) を使用
            phash = imagehash.phash(img, hash_size=8)  # 64-bit hash
            return str(phash)
        except Exception as e:
            print(f"Hash calculation failed: {e}")
            return None

    def find_duplicates(
        self,
        photo_hashes: List[Tuple[str, str]]
    ) -> List[Dict]:
        """
        重複グループを検出

        Args:
            photo_hashes: [(photo_id, hash_value), ...]

        Returns:
            [
                {
                    'primary_id': str,
                    'duplicate_ids': [str, ...],
                    'similarity_scores': [float, ...]
                },
                ...
            ]
        """
        duplicates = []
        processed = set()

        for i, (id1, hash1) in enumerate(photo_hashes):
            if id1 in processed:
                continue

            group = {
                'primary_id': id1,
                'duplicate_ids': [],
                'similarity_scores': []
            }

            hash1_obj = imagehash.hex_to_hash(hash1)

            for j, (id2, hash2) in enumerate(photo_hashes[i+1:], start=i+1):
                if id2 in processed:
                    continue

                hash2_obj = imagehash.hex_to_hash(hash2)
                hamming_distance = hash1_obj - hash2_obj

                if hamming_distance <= self.threshold:
                    group['duplicate_ids'].append(id2)
                    group['similarity_scores'].append(
                        1 - (hamming_distance / 64)  # 0-1の類似度スコア
                    )
                    processed.add(id2)

            if group['duplicate_ids']:
                duplicates.append(group)
                processed.add(id1)

        return duplicates

    def compare_two_images(
        self,
        image_path1: str,
        image_path2: str
    ) -> Dict:
        """2枚の画像の類似度を計算"""

        hash1 = self.calculate_hash(image_path1)
        hash2 = self.calculate_hash(image_path2)

        if not hash1 or not hash2:
            return {'error': 'Hash calculation failed'}

        hash1_obj = imagehash.hex_to_hash(hash1)
        hash2_obj = imagehash.hex_to_hash(hash2)

        hamming_distance = hash1_obj - hash2_obj
        similarity = 1 - (hamming_distance / 64)

        return {
            'hamming_distance': hamming_distance,
            'similarity_score': round(similarity, 4),
            'is_duplicate': hamming_distance <= self.threshold,
            'confidence': 'high' if hamming_distance <= 3 else 'medium' if hamming_distance <= 8 else 'low'
        }
```

---

## 6. 学習データ準備計画

### 6.1 データ収集戦略

#### Phase 1: 初期データセット構築（Month 1-2）

| データソース | 目標枚数 | 収集方法 |
|-------------|---------|---------|
| **過去プロジェクト** | 5,000枚 | 既存写真の整理・ラベリング |
| **サンプル写真撮影** | 1,000枚 | 模擬工事現場での撮影 |
| **パートナー企業** | 3,000枚 | データ提供契約 |
| **合計** | 9,000枚 | - |

#### Phase 2: データ拡張（Month 3-4）

```python
# scripts/data_augmentation.py
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

def augment_training_data(input_dir: str, output_dir: str, augmentation_factor: int = 5):
    """学習データの拡張"""

    datagen = ImageDataGenerator(
        rotation_range=15,           # 回転
        width_shift_range=0.1,       # 水平シフト
        height_shift_range=0.1,      # 垂直シフト
        shear_range=0.1,            # せん断変換
        zoom_range=0.1,             # ズーム
        horizontal_flip=True,        # 水平反転
        brightness_range=[0.8, 1.2], # 明るさ調整
        fill_mode='nearest'
    )

    # 各カテゴリごとに処理
    for category in os.listdir(input_dir):
        category_path = os.path.join(input_dir, category)
        output_category_path = os.path.join(output_dir, category)
        os.makedirs(output_category_path, exist_ok=True)

        for img_file in os.listdir(category_path):
            img_path = os.path.join(category_path, img_file)
            img = keras.preprocessing.image.load_img(img_path)
            img_array = keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, 0)

            # 拡張画像生成
            i = 0
            for batch in datagen.flow(
                img_array,
                batch_size=1,
                save_to_dir=output_category_path,
                save_prefix=f"aug_{img_file.split('.')[0]}",
                save_format='jpg'
            ):
                i += 1
                if i >= augmentation_factor:
                    break

    print(f"Data augmentation completed: {augmentation_factor}x increase")
```

### 6.2 アノテーション計画

#### ラベリングツール選定

**推奨**: Label Studio（オープンソース）

```bash
# Label Studio セットアップ
pip install label-studio

# 起動
label-studio start --port 8080

# プロジェクト作成
# UI上で以下を設定:
# - タスクタイプ: Image Classification
# - ラベル: 8カテゴリ（着手前及び完成写真、施工状況写真、...）
```

#### アノテーション作業計画

| 作業 | 担当 | 期間 | 枚数/日 |
|------|------|------|---------|
| **初期ラベリング** | 現場監督2名 | 2週間 | 300枚 |
| **品質チェック** | AI担当1名 | 1週間 | 500枚 |
| **追加ラベリング** | クラウドワーカー | 4週間 | 200枚 |

---

## 7. モデル評価・改善計画

### 7.1 評価指標

```python
# evaluation/metrics.py
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import numpy as np

class ModelEvaluator:
    """モデル評価クラス"""

    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        categories: List[str]
    ) -> Dict:
        """分類モデル評価"""

        # 基本指標
        accuracy = accuracy_score(y_true, y_pred)

        # カテゴリ別の精度・再現率・F1スコア
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true,
            y_pred,
            average=None,
            labels=range(len(categories))
        )

        # 混同行列
        cm = confusion_matrix(y_true, y_pred)

        results = {
            'overall_accuracy': round(accuracy, 4),
            'macro_f1': round(np.mean(f1), 4),
            'per_class_metrics': []
        }

        for i, category in enumerate(categories):
            results['per_class_metrics'].append({
                'category': category,
                'precision': round(precision[i], 4),
                'recall': round(recall[i], 4),
                'f1_score': round(f1[i], 4),
                'support': int(support[i])
            })

        results['confusion_matrix'] = cm.tolist()

        return results

    def plot_confusion_matrix(self, cm: np.ndarray, categories: List[str]):
        """混同行列の可視化"""
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=categories,
            yticklabels=categories
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        plt.close()
```

### 7.2 A/Bテスト計画

```python
# services/ab_testing_service.py
import random
from typing import Dict

class ABTestingService:
    """A/Bテストサービス"""

    def __init__(self):
        self.model_versions = {
            'A': 'rekognition_v1',  # 既存モデル
            'B': 'custom_cnn_v1',   # 新モデル
        }
        self.split_ratio = 0.5  # 50/50分割

    def get_model_version(self, user_id: str) -> str:
        """ユーザーにモデルバージョンを割り当て"""

        # ユーザーIDベースの決定論的割り当て
        hash_value = hash(user_id)
        if hash_value % 100 < self.split_ratio * 100:
            return 'A'
        else:
            return 'B'

    def track_prediction(
        self,
        user_id: str,
        photo_id: str,
        model_version: str,
        prediction: Dict,
        user_feedback: Optional[str] = None
    ):
        """予測結果とフィードバックを記録"""

        # DynamoDBまたはCloudWatchに記録
        metrics = {
            'user_id': user_id,
            'photo_id': photo_id,
            'model_version': model_version,
            'prediction': prediction,
            'user_feedback': user_feedback,
            'timestamp': datetime.utcnow().isoformat()
        }

        # ... 記録処理

    def analyze_results(self) -> Dict:
        """A/Bテスト結果分析"""

        # モデルAとBの比較
        results = {
            'model_A': {
                'accuracy': 0.82,
                'avg_confidence': 0.78,
                'user_satisfaction': 0.85
            },
            'model_B': {
                'accuracy': 0.87,
                'avg_confidence': 0.83,
                'user_satisfaction': 0.90
            },
            'winner': 'B',
            'improvement': '+5% accuracy'
        }

        return results
```

---

## 8. 推論パフォーマンス最適化

### 8.1 モデル軽量化

```python
# optimization/model_optimization.py
import tensorflow as tf

class ModelOptimizer:
    """モデル最適化クラス"""

    def quantize_model(self, model_path: str, output_path: str):
        """モデル量子化（INT8）"""

        # TensorFlow Liteコンバータ
        converter = tf.lite.TFLiteConverter.from_saved_model(model_path)

        # 量子化設定
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.int8]

        # 変換
        tflite_model = converter.convert()

        # 保存
        with open(output_path, 'wb') as f:
            f.write(tflite_model)

        print(f"Quantized model saved: {output_path}")

        # サイズ削減効果を表示
        original_size = os.path.getsize(model_path)
        quantized_size = os.path.getsize(output_path)
        reduction = (1 - quantized_size / original_size) * 100

        print(f"Model size reduction: {reduction:.1f}%")

    def prune_model(self, model: keras.Model, target_sparsity: float = 0.5):
        """モデル枝刈り"""

        import tensorflow_model_optimization as tfmot

        # 枝刈り設定
        pruning_schedule = tfmot.sparsity.keras.PolynomialDecay(
            initial_sparsity=0.0,
            final_sparsity=target_sparsity,
            begin_step=0,
            end_step=1000
        )

        # モデルに適用
        pruned_model = tfmot.sparsity.keras.prune_low_magnitude(
            model,
            pruning_schedule=pruning_schedule
        )

        return pruned_model
```

### 8.2 推論キャッシング

```python
# services/inference_cache_service.py
import redis
import pickle
from typing import Dict, Optional

class InferenceCacheService:
    """推論結果キャッシングサービス"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=False
        )
        self.cache_ttl = 3600 * 24 * 7  # 7日間

    def get_cached_result(self, photo_hash: str) -> Optional[Dict]:
        """キャッシュから推論結果を取得"""

        cache_key = f"inference:{photo_hash}"
        cached = self.redis_client.get(cache_key)

        if cached:
            return pickle.loads(cached)

        return None

    def cache_result(self, photo_hash: str, result: Dict):
        """推論結果をキャッシュ"""

        cache_key = f"inference:{photo_hash}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            pickle.dumps(result)
        )

    def invalidate_cache(self, photo_hash: str):
        """キャッシュ無効化"""
        cache_key = f"inference:{photo_hash}"
        self.redis_client.delete(cache_key)
```

### 8.3 バッチ推論

```python
# services/batch_inference_service.py
from typing import List, Dict
import numpy as np

class BatchInferenceService:
    """バッチ推論サービス"""

    def __init__(self, model, batch_size: int = 32):
        self.model = model
        self.batch_size = batch_size

    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """バッチ推論（高速化）"""

        results = []

        # バッチ単位で処理
        for i in range(0, len(image_paths), self.batch_size):
            batch_paths = image_paths[i:i + self.batch_size]

            # 画像読み込み
            batch_images = []
            for path in batch_paths:
                img = keras.preprocessing.image.load_img(
                    path,
                    target_size=(224, 224)
                )
                img_array = keras.preprocessing.image.img_to_array(img) / 255.0
                batch_images.append(img_array)

            batch_images = np.array(batch_images)

            # バッチ推論
            predictions = self.model.predict(batch_images)

            # 結果を個別に分割
            for j, pred in enumerate(predictions):
                results.append({
                    'image_path': batch_paths[j],
                    'prediction': pred.tolist()
                })

        return results
```

---

**次のセクション**: コスト見積もり、リスク管理、実装ガイドラインの各ドキュメントを続けて作成します。
