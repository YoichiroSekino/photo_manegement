# リスク管理計画書

**バージョン**: 1.0
**作成日**: 2025-11-02

---

## 目次

1. [リスク管理概要](#1-リスク管理概要)
2. [技術リスク](#2-技術リスク)
3. [スケジュールリスク](#3-スケジュールリスク)
4. [コストリスク](#4-コストリスク)
5. [品質リスク](#5-品質リスク)
6. [運用リスク](#6-運用リスク)
7. [リスク監視計画](#7-リスク監視計画)

---

## 1. リスク管理概要

### 1.1 リスク評価マトリクス

```
影響度 →  小     中     大     甚大
発生確率
  ↓
高      中     高     高     最高
中      低     中     高     高
低      低     低     中     中
極小    低     低     低     中
```

### 1.2 リスク対応戦略

| 戦略 | 説明 | 適用例 |
|------|------|--------|
| **回避** | リスク要因を排除 | 複雑な技術を避ける |
| **軽減** | 影響または発生確率を下げる | テスト強化、予備設計 |
| **転嫁** | リスクを第三者に移転 | 保険、外部委託 |
| **受容** | リスクを認識し受け入れる | 小規模リスクの受容 |

---

## 2. 技術リスク

### 2.1 AI/ML精度不足

**リスクID**: TR-001
**カテゴリ**: 技術リスク
**発生確率**: 中（40%）
**影響度**: 大

#### リスク内容
- OCR認識精度が目標（85%）に達しない
- 画像分類精度が低い（<75%）
- 手書き文字の認識が困難

#### 影響
- ユーザー満足度低下
- 手動修正作業の増加
- システムの価値低減

#### 対策

**予防策**:
1. **プロトタイプ検証**（Month 1-2）
   ```python
   # 早期検証スクリプト
   def validate_ocr_accuracy(sample_images):
       results = []
       for img in sample_images:
           ocr_result = textract.detect_text(img)
           manual_truth = load_ground_truth(img)
           accuracy = calculate_accuracy(ocr_result, manual_truth)
           results.append(accuracy)

       avg_accuracy = sum(results) / len(results)
       if avg_accuracy < 0.80:
           raise Warning("OCR精度目標未達")
   ```

2. **学習データ品質向上**
   - 高品質なラベルデータ（ダブルチェック）
   - データ拡張（Augmentation）
   - 不均衡データの調整

3. **代替手段の準備**
   - Amazon Textract + Google Cloud Vision API併用
   - カスタムOCRモデルの開発

**緩和策**:
- ユーザーフィードバック機能
- 手動修正UIの充実
- 段階的精度向上（継続学習）

**コンティンジェンシープラン**:
```
IF OCR精度 < 70%
  THEN
    - 手動確認フローを必須化
    - 外部OCRサービスの併用
    - リリース時期の延期（最大2ヶ月）
```

---

### 2.2 大量データ処理性能不足

**リスクID**: TR-002
**発生確率**: 中（30%）
**影響度**: 大

#### リスク内容
- 10,000枚同時アップロードで処理遅延
- データベースクエリが遅い（>3秒）
- Lambda タイムアウト（15分制限）

#### 影響
- ユーザー体験の悪化
- システムダウン
- 追加インフラコスト

#### 対策

**予防策**:
1. **負荷テスト実施**（Phase 1完了時）
   ```bash
   # Locustによる負荷テスト
   locust -f load_test.py \
     --users 100 \
     --spawn-rate 10 \
     --run-time 10m \
     --host https://api.example.com
   ```

2. **アーキテクチャ最適化**
   - S3 Multipart Upload
   - Lambda並列実行
   - RDSリードレプリカ
   - ElastiCache導入

3. **パフォーマンス監視**
   ```python
   # CloudWatch メトリクス
   metrics = {
       'upload_duration': 'P99 < 10s',
       'ocr_processing': 'P99 < 5s',
       'search_query': 'P99 < 500ms',
   }
   ```

**緩和策**:
- 処理キュー（SQS）による非同期化
- バッチ処理時間の制限（夜間処理推奨）
- プログレッシブアップロード

---

### 2.3 AWS サービス障害

**リスクID**: TR-003
**発生確率**: 低（10%）
**影響度**: 甚大

#### リスク内容
- S3, Lambda, RDSの障害
- リージョン障害

#### 影響
- システム全停止
- データ損失リスク
- ビジネス停止

#### 対策

**予防策**:
1. **Multi-AZ構成**
   ```terraform
   resource "aws_db_instance" "main" {
     multi_az               = true
     backup_retention_period = 7
     # ...
   }
   ```

2. **自動バックアップ**
   - RDS: 7日間保持
   - S3: バージョニング有効化
   - DynamoDB: PITR有効化

3. **監視・アラート**
   ```yaml
   # CloudWatch Alarm
   alarms:
     - name: RDS-CPU-High
       threshold: 80%
       actions: [SNS通知, 自動スケール]

     - name: Lambda-Error-Rate
       threshold: 5%
       actions: [SNS通知, ロールバック]
   ```

**緩和策**:
- SLA 99.9%（月間43分のダウンタイム許容）
- ステータスページ設置
- 顧客への事前通知

**コンティンジェンシープラン**:
```
障害発生時の対応手順:
1. 障害検知（5分以内）
2. ユーザー通知（10分以内）
3. 原因調査開始（即時）
4. 復旧作業開始（30分以内）
5. サービス復旧確認（1時間以内）
6. 事後報告書作成（24時間以内）
```

---

## 3. スケジュールリスク

### 3.1 開発遅延

**リスクID**: SR-001
**発生確率**: 高（60%）
**影響度**: 中

#### リスク内容
- フェーズ完了が遅延
- 機能実装の見積もり誤差
- リソース不足

#### 影響
- リリース時期の遅れ
- コスト超過
- ビジネス機会損失

#### 対策

**予防策**:
1. **バッファ確保**
   - 各フェーズに20%のバッファ
   - クリティカルパスの特定

2. **スプリント管理**（2週間単位）
   ```
   Week 1-2: Sprint 1
     - 計画: 1日
     - 開発: 8日
     - レビュー: 0.5日
     - 振り返り: 0.5日

   進捗指標:
     - ベロシティ: 目標80ポイント/スプリント
     - バーンダウンチャート
   ```

3. **早期警戒指標**
   ```
   黄色信号:
     - スプリントベロシティ < 70%
     - バグ密度 > 5件/100行

   赤色信号:
     - 2スプリント連続で目標未達
     - クリティカルバグ未解決
   ```

**緩和策**:
- 機能の優先順位付け（MoSCoW法）
  - Must: 必須機能
  - Should: 重要機能
  - Could: あれば良い機能
  - Won't: 今回は対象外
- MVP範囲の縮小

**コンティンジェンシープラン**:
```
IF 遅延 > 2週間
  THEN
    - Phase 4（連携・拡張）を延期
    - リソース追加（外部委託）
    - リリース日の再設定
```

---

## 4. コストリスク

### 4.1 AWS コスト超過

**リスクID**: CR-001
**発生確率**: 中（40%）
**影響度**: 中

#### リスク内容
- 想定以上のトラフィック
- Textract/Rekognition利用量増加
- RDSスケールアップ

#### 影響
- 予算超過（+30-50%）
- キャッシュフロー悪化

#### 対策

**予防策**:
1. **コスト予算アラート**
   ```bash
   # AWS Budgets設定
   aws budgets create-budget \
     --account-id 123456789012 \
     --budget file://monthly-budget.json \
     --notifications-with-subscribers file://notifications.json

   # 閾値:
   # - 80%: 警告メール
   # - 100%: 緊急アラート + 自動スケールダウン検討
   ```

2. **コスト監視ダッシュボード**
   ```python
   # 日次コストレポート
   def generate_cost_report():
       services = ['S3', 'Lambda', 'RDS', 'Textract', 'Rekognition']
       for service in services:
           cost = get_service_cost(service, period='daily')
           if cost > budget[service] * 1.2:
               alert(f"{service} cost exceeded: ${cost}")
   ```

3. **使用量制限**
   - API rate limiting: 100req/min/user
   - アップロード上限: 10,000枚/日
   - Textract月間上限: 200,000ページ

**緩和策**:
- Reserved Instances（25%削減）
- S3ライフサイクルポリシー
- 不要リソースの自動削除

---

## 5. 品質リスク

### 5.1 国交省基準非準拠

**リスクID**: QR-001
**発生確率**: 中（30%）
**影響度**: 甚大

#### リスク内容
- PHOTO.XML形式エラー
- ファイル命名規則違反
- 必須項目の欠落

#### 影響
- 電子納品の拒否
- システムの信頼性喪失
- 再開発コスト

#### 対策

**予防策**:
1. **バリデーション強化**
   ```python
   # 厳格なバリデーター
   class PHOTO05Validator:
       def validate_xml(self, xml_path):
           errors = []

           # DTD準拠チェック
           if not self.validate_dtd(xml_path):
               errors.append("DTD validation failed")

           # 必須項目チェック
           required_fields = [
               '写真フォルダ名',
               '適用要領基準',
               # ...
           ]
           for field in required_fields:
               if not self.check_field_exists(xml_path, field):
                   errors.append(f"Missing required field: {field}")

           # 文字数制限チェック
           # ...

           return len(errors) == 0, errors
   ```

2. **自動テスト**
   ```python
   def test_photo_xml_compliance():
       """PHOTO05.DTD準拠テスト"""
       xml = generate_photo_xml(sample_photos)

       # DTD検証
       assert validate_against_dtd(xml, 'PHOTO05.DTD')

       # 文字コードチェック
       assert get_encoding(xml) == 'shift_jis'

       # ファイル名形式チェック
       for photo in sample_photos:
           assert re.match(r'^P\d{7}\.JPG$', photo.filename)
   ```

3. **専門家レビュー**
   - 建設業界経験者によるレビュー
   - 実際の納品物でのテスト

**緩和策**:
- 手動チェックリスト
- 修正ツールの提供

---

## 6. 運用リスク

### 6.1 セキュリティ侵害

**リスクID**: OR-001
**発生確率**: 低（15%）
**影響度**: 甚大

#### リスク内容
- 不正アクセス
- データ漏洩
- ランサムウェア攻撃

#### 影響
- 機密情報流出
- 法的責任
- 信用失墜

#### 対策

**予防策**:
1. **セキュリティ対策**
   ```yaml
   # セキュリティチェックリスト
   - [ ] AWS WAF導入
   - [ ] Multi-factor Authentication
   - [ ] 暗号化（保存時・転送時）
   - [ ] IAMロール最小権限
   - [ ] セキュリティグループ設定
   - [ ] ログ監視（CloudTrail）
   - [ ] 脆弱性スキャン（月次）
   ```

2. **侵入検知**
   ```python
   # AWS GuardDuty + カスタムアラート
   def detect_anomaly(event):
       if event['severity'] >= 7:  # High severity
           send_alert(
               channel='security-team',
               message=f"Security threat detected: {event}"
           )
           auto_block_ip(event['source_ip'])
   ```

3. **データバックアップ**
   - 日次バックアップ（7日保持）
   - 週次バックアップ（4週保持）
   - 月次バックアップ（12ヶ月保持）

**緩和策**:
- インシデント対応計画（IRP）
- サイバー保険加入
- 情報開示ポリシー

**インシデント対応手順**:
```
1. 検知（即時）
   └→ 自動アラート + 担当者通知

2. 封じ込め（30分以内）
   └→ 侵害範囲の特定
   └→ アクセス遮断

3. 根絶（2時間以内）
   └→ 脆弱性の修正
   └→ パスワードリセット

4. 復旧（4時間以内）
   └→ サービス再開
   └→ 監視強化

5. 事後対応（24時間以内）
   └→ インシデントレポート
   └→ ユーザー通知
   └→ 再発防止策
```

---

## 7. リスク監視計画

### 7.1 定期レビュー

| 頻度 | 対象リスク | 参加者 | 成果物 |
|------|-----------|--------|--------|
| **週次** | 高リスク（赤） | PM, Tech Lead | リスクステータスレポート |
| **月次** | 全リスク | 全チーム | リスク管理簿更新 |
| **四半期** | 戦略的リスク | 経営層 | リスク対応計画見直し |

### 7.2 リスク指標（KRI）

```python
# Key Risk Indicators
KRI = {
    'technical': {
        'ocr_accuracy': {
            'current': 0.87,
            'target': 0.85,
            'threshold': 0.80,  # 下回ったらアラート
        },
        'system_uptime': {
            'current': 0.998,
            'target': 0.999,
            'threshold': 0.995,
        }
    },
    'schedule': {
        'sprint_velocity': {
            'current': 75,
            'target': 80,
            'threshold': 60,
        },
        'bug_density': {
            'current': 3.5,  # bugs per 100 LOC
            'target': 2.0,
            'threshold': 5.0,
        }
    },
    'cost': {
        'aws_monthly_cost': {
            'current': 180000,  # JPY
            'budget': 200000,
            'threshold': 240000,  # 120% of budget
        }
    }
}
```

### 7.3 エスカレーションプロセス

```
リスク発生
    │
    ▼
├─ 低リスク → チーム内で対処
│
├─ 中リスク → PM報告 → 週次レビュー
│
└─ 高リスク → 即時報告 → 緊急ミーティング → 経営層判断
```

---

**本リスク管理計画は、プロジェクト進行に応じて継続的に更新されます。**
