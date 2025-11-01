import { validateFile, validateFiles, ValidationError } from '../fileValidator';

describe('fileValidator', () => {
  describe('validateFile', () => {
    it('有効なJPEGファイルをパスする', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const result = validateFile(file);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('有効なTIFFファイルをパスする', () => {
      const file = new File(['content'], 'test.tiff', { type: 'image/tiff' });
      const result = validateFile(file);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('無効なファイル形式を拒否する', () => {
      const file = new File(['content'], 'test.png', { type: 'image/png' });
      const result = validateFile(file);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(ValidationError.INVALID_FILE_TYPE);
    });

    it('大きすぎるファイルを拒否する（10MB超）', () => {
      // 11MBのファイルを模擬
      const largeContent = new Array(11 * 1024 * 1024).fill('a').join('');
      const file = new File([largeContent], 'large.jpg', { type: 'image/jpeg' });

      const result = validateFile(file, { maxSize: 10 * 1024 * 1024 });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(ValidationError.FILE_TOO_LARGE);
    });

    it('ファイル名が長すぎる場合を拒否する', () => {
      const longName = 'a'.repeat(256) + '.jpg';
      const file = new File(['content'], longName, { type: 'image/jpeg' });

      const result = validateFile(file);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(ValidationError.FILENAME_TOO_LONG);
    });

    it('ファイル名に無効な文字が含まれている場合を拒否する', () => {
      const file = new File(['content'], 'test<>.jpg', { type: 'image/jpeg' });
      const result = validateFile(file);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(ValidationError.INVALID_FILENAME);
    });

    it('複数のエラーを返す', () => {
      const largeContent = new Array(11 * 1024 * 1024).fill('a').join('');
      const file = new File([largeContent], 'test.png', { type: 'image/png' });

      const result = validateFile(file, { maxSize: 10 * 1024 * 1024 });
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(1);
    });
  });

  describe('validateFiles', () => {
    it('全てのファイルが有効な場合', () => {
      const files = [
        new File(['content1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      ];

      const results = validateFiles(files);
      expect(results.every((r) => r.isValid)).toBe(true);
    });

    it('一部のファイルが無効な場合', () => {
      const files = [
        new File(['content1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'test2.png', { type: 'image/png' }),
      ];

      const results = validateFiles(files);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(false);
    });

    it('ファイル数が上限を超える場合', () => {
      const files = Array.from({ length: 15 }, (_, i) =>
        new File(['content'], `test${i}.jpg`, { type: 'image/jpeg' })
      );

      const results = validateFiles(files, { maxFiles: 10 });
      expect(results).toHaveLength(10);
    });
  });
});
