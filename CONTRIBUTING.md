# 貢献ガイドライン

工事写真自動整理システムへの貢献方法

## 🎯 開発方針

### 重要原則

1. **日本語でのコミュニケーション**: ドキュメント、コメント、GitHub Issueは日本語で記述
2. **テスト駆動開発（TDD）**: テストを先に書き、その後実装
3. **小さなタスク**: 1つのIssueは最大5人日（40時間）、理想は1人日単位
4. **順次実行**: Issueを1つずつ完了させる
5. **コードレビュー**: 全てのPRは最低1人のレビューが必要

## 🔄 開発フロー

### 1. Issueの選択

```bash
# 未着手のIssueを確認
gh issue list --state open --label "Phase 1"

# Issueを自分にアサイン
gh issue edit <issue-number> --add-assignee @me
```

### 2. ブランチの作成

```bash
# ブランチ命名規則: feature/#<issue-number>-<short-description>
git checkout -b feature/#1-project-setup

# バグ修正の場合: bugfix/#<issue-number>-<short-description>
git checkout -b bugfix/#42-fix-upload-error
```

### 3. TDDサイクル

#### Red（失敗するテストを書く）

```typescript
// frontend/components/upload/__tests__/DragDropZone.test.tsx
describe('DragDropZone', () => {
  it('should accept JPEG files', () => {
    // テストを先に書く（この時点では実装がないので失敗する）
    const { getByTestId } = render(<DragDropZone />);
    const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });

    // ファイルをドロップ
    fireEvent.drop(getByTestId('drop-zone'), { dataTransfer: { files: [file] } });

    // ファイルが受け入れられることを期待
    expect(getByTestId('file-list')).toHaveTextContent('test.jpg');
  });
});
```

#### Green（最小限の実装でテストをパス）

```typescript
// frontend/components/upload/DragDropZone.tsx
export const DragDropZone: FC = () => {
  const [files, setFiles] = useState<File[]>([]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
  };

  return (
    <div data-testid="drop-zone" onDrop={handleDrop}>
      <ul data-testid="file-list">
        {files.map(file => <li key={file.name}>{file.name}</li>)}
      </ul>
    </div>
  );
};
```

#### Refactor（リファクタリング）

```typescript
// 抽出、整理、最適化
const useFileUpload = () => {
  const [files, setFiles] = useState<File[]>([]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
  }, []);

  return { files, handleDrop };
};
```

### 4. コミット

```bash
# ステージング
git add .

# コミットメッセージ規約
# <type>: <subject>
#
# <body>
#
# Issue: #<issue-number>

git commit -m "feat: ドラッグ&ドロップゾーンコンポーネント実装

- ファイルドロップ機能
- JPEG/TIFF形式のバリデーション
- プレビュー表示

Issue: #1"
```

#### コミットタイプ

- `feat`: 新機能
- `fix`: バグ修正
- `test`: テスト追加・修正
- `refactor`: リファクタリング
- `docs`: ドキュメント
- `style`: コードフォーマット
- `chore`: ビルド・設定変更

### 5. プッシュとPR作成

```bash
# リモートにプッシュ
git push origin feature/#1-project-setup

# PRを作成
gh pr create --title "feat: プロジェクトセットアップ・環境構築" \
  --body "## 概要
Issue #1 の実装

## 変更内容
- プロジェクトディレクトリ構造作成
- .gitignore設定
- VS Code設定ファイル
- SETUP.md, CONTRIBUTING.md作成

## テスト
- [ ] ローカル環境で動作確認
- [ ] テスト全件パス

## チェックリスト
- [x] TDDで実装
- [x] コメントは日本語
- [x] テストカバレッジ80%以上
- [ ] ドキュメント更新

Closes #1"
```

### 6. コードレビュー

- 自動テスト（GitHub Actions）が全てパスすることを確認
- レビュワーからのフィードバックに対応
- 承認後、マージ

### 7. ブランチのクリーンアップ

```bash
# ローカルブランチ削除
git branch -d feature/#1-project-setup

# リモートブランチ削除（GitHub UIで自動削除推奨）
git push origin --delete feature/#1-project-setup
```

## 📝 コーディング規約

### TypeScript / React

```typescript
// ✅ 良い例
interface PhotoCardProps {
  photo: Photo;
  onSelect?: (id: string) => void;
}

export const PhotoCard: FC<PhotoCardProps> = ({ photo, onSelect }) => {
  // フックを先頭に
  const [isHovered, setIsHovered] = useState(false);

  // イベントハンドラー
  const handleClick = useCallback(() => {
    onSelect?.(photo.id);
  }, [photo.id, onSelect]);

  // 早期リターン
  if (!photo) return null;

  // JSX
  return <div onClick={handleClick}>{photo.title}</div>;
};

// ❌ 悪い例
export default function PhotoCard(props) { // Propsの型なし
  if (!props.photo) return null;
  const [isHovered, setIsHovered] = useState(false); // フックの位置

  return <div onClick={() => props.onSelect(props.photo.id)}>{props.photo.title}</div>;
}
```

### Python / FastAPI

```python
# ✅ 良い例
from typing import Optional
from pydantic import BaseModel

class Photo(BaseModel):
    """写真データモデル"""

    id: str
    title: str
    file_path: str
    shooting_date: Optional[str] = None

    class Config:
        """Pydantic設定"""
        orm_mode = True

# ❌ 悪い例
class Photo:  # BaseModelを継承していない
    def __init__(self, id, title, file_path):  # 型ヒントなし
        self.id = id
        self.title = title
        self.file_path = file_path
```

## 🧪 テスト要件

### カバレッジ目標

- **全体**: 80%以上
- **クリティカルパス**: 100%
- **新規コード**: 90%以上

### テストピラミッド

```
    E2E (10%)
   /          \
  Integration (30%)
 /                  \
Unit Tests (60%)
```

### 必須テスト

- [ ] 正常系テスト
- [ ] 異常系テスト（エラーハンドリング）
- [ ] 境界値テスト
- [ ] バリデーションテスト

## 🔍 コードレビューチェックリスト

### レビュワー向け

- [ ] コードが要件を満たしているか
- [ ] TDDで実装されているか
- [ ] テストが十分か（カバレッジ80%以上）
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンス上の問題がないか
- [ ] コメントが適切か（日本語）
- [ ] 命名規則に従っているか

### 作成者向け

- [ ] 自己レビュー済み
- [ ] テスト全件パス
- [ ] リンター警告なし
- [ ] コンフリクト解消済み
- [ ] ドキュメント更新済み

## 🚫 やってはいけないこと

1. **テストなしでコード実装**: 必ずテストを先に書く
2. **大きなPR**: 500行以上の変更は分割する
3. **直接mainにプッシュ**: 必ずPRを経由
4. **テスト失敗でマージ**: CI/CDが全てグリーンであること
5. **レビューなしでマージ**: 最低1人の承認が必要

## 📚 参考資料

- [実装ガイドライン](./docs/implementation-guide.md)
- [技術アーキテクチャ](./docs/technical-architecture.md)
- [開発計画](./docs/development-plan.md)

## 🆘 ヘルプ

質問がある場合：

1. [GitHub Discussions](https://github.com/YoichiroSekino/photo_manegement/discussions)で質問
2. Issueにコメント
3. プロジェクトメンテナーに連絡

---

**更新日**: 2025-11-02
