/**
 * ファイルバリデーションモジュール
 * 国土交通省「デジタル写真管理情報基準」に準拠
 */

export enum ValidationError {
  INVALID_FILE_TYPE = 'ファイル形式が無効です。JPEG、TIFF形式のみ対応しています。',
  FILE_TOO_LARGE = 'ファイルサイズが大きすぎます。',
  FILENAME_TOO_LONG = 'ファイル名が長すぎます（最大255文字）。',
  INVALID_FILENAME = 'ファイル名に使用できない文字が含まれています。',
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  file: File;
}

export interface ValidationOptions {
  maxSize?: number; // バイト単位（デフォルト: 10MB）
  maxFiles?: number; // 最大ファイル数
  allowedTypes?: string[]; // 許可するMIMEタイプ
}

const DEFAULT_OPTIONS: Required<Omit<ValidationOptions, 'maxFiles'>> = {
  maxSize: 10 * 1024 * 1024, // 10MB
  allowedTypes: ['image/jpeg', 'image/tiff'],
};

/**
 * 単一ファイルのバリデーション
 *
 * @param file - 検証するファイル
 * @param options - バリデーションオプション
 * @returns バリデーション結果
 */
export function validateFile(
  file: File,
  options: ValidationOptions = {}
): ValidationResult {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const errors: ValidationError[] = [];

  // ファイル形式チェック
  if (!opts.allowedTypes.includes(file.type)) {
    errors.push(ValidationError.INVALID_FILE_TYPE);
  }

  // ファイルサイズチェック
  if (file.size > opts.maxSize) {
    errors.push(ValidationError.FILE_TOO_LARGE);
  }

  // ファイル名の長さチェック
  if (file.name.length > 255) {
    errors.push(ValidationError.FILENAME_TOO_LONG);
  }

  // ファイル名の文字チェック（無効な文字を含まないか）
  const invalidCharsRegex = /[<>:"|?*]/;
  if (invalidCharsRegex.test(file.name)) {
    errors.push(ValidationError.INVALID_FILENAME);
  }

  return {
    isValid: errors.length === 0,
    errors,
    file,
  };
}

/**
 * 複数ファイルのバリデーション
 *
 * @param files - 検証するファイルの配列
 * @param options - バリデーションオプション
 * @returns バリデーション結果の配列
 */
export function validateFiles(
  files: File[],
  options: ValidationOptions = {}
): ValidationResult[] {
  // ファイル数制限がある場合は先頭から制限数までのみ検証
  const filesToValidate = options.maxFiles
    ? files.slice(0, options.maxFiles)
    : files;

  return filesToValidate.map((file) => validateFile(file, options));
}

/**
 * バリデーション結果から有効なファイルのみを抽出
 *
 * @param results - バリデーション結果の配列
 * @returns 有効なファイルの配列
 */
export function getValidFiles(results: ValidationResult[]): File[] {
  return results.filter((result) => result.isValid).map((result) => result.file);
}

/**
 * バリデーション結果からエラーメッセージを生成
 *
 * @param results - バリデーション結果の配列
 * @returns エラーメッセージの配列
 */
export function getErrorMessages(results: ValidationResult[]): string[] {
  return results
    .filter((result) => !result.isValid)
    .flatMap((result) =>
      result.errors.map((error) => `${result.file.name}: ${error}`)
    );
}
