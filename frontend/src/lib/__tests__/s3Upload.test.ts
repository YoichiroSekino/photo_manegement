/**
 * S3アップロードライブラリのテスト
 */

import { PresignedUploader, UploadProgress } from '../s3Upload';

// グローバルfetchのモック
global.fetch = jest.fn();

describe('PresignedUploader', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('uploadWithPresignedUrl', () => {
    it('should successfully upload a file with presigned URL', async () => {
      // モックファイル
      const file = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      const endpoint = '/api/v1/photos/upload';

      // モックレスポンス
      const mockPresignedResponse = {
        presignedUrl: 'https://s3.amazonaws.com/test-bucket/test.jpg?signature=abc',
        key: 'photos/test.jpg',
        bucket: 'test-bucket',
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPresignedResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
        });

      // アップロード実行
      const result = await PresignedUploader.uploadWithPresignedUrl(file, endpoint);

      // 検証
      expect(result).toEqual({
        key: 'photos/test.jpg',
        location: 'https://test-bucket.s3.amazonaws.com/photos/test.jpg',
        bucket: 'test-bucket',
      });

      // fetch呼び出しの検証
      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(global.fetch).toHaveBeenNthCalledWith(1, endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName: 'test.jpg',
          fileSize: file.size,
          mimeType: 'image/jpeg',
        }),
      });
    });

    it('should call progress callback during upload', async () => {
      const file = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      const endpoint = '/api/v1/photos/upload';
      const progressCallback = jest.fn();

      const mockPresignedResponse = {
        presignedUrl: 'https://s3.amazonaws.com/test-bucket/test.jpg',
        key: 'photos/test.jpg',
        bucket: 'test-bucket',
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPresignedResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
        });

      await PresignedUploader.uploadWithPresignedUrl(file, endpoint, progressCallback);

      // 進捗コールバックが呼ばれたことを確認
      expect(progressCallback).toHaveBeenCalled();
      const lastCall = progressCallback.mock.calls[progressCallback.mock.calls.length - 1][0];
      expect(lastCall.status).toBe('completed');
      expect(lastCall.percentage).toBe(100);
    });

    it('should handle presigned URL fetch error', async () => {
      const file = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      const endpoint = '/api/v1/photos/upload';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
      });

      await expect(
        PresignedUploader.uploadWithPresignedUrl(file, endpoint)
      ).rejects.toThrow('Failed to get presigned URL');
    });

    it('should handle S3 upload error', async () => {
      const file = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      const endpoint = '/api/v1/photos/upload';

      const mockPresignedResponse = {
        presignedUrl: 'https://s3.amazonaws.com/test-bucket/test.jpg',
        key: 'photos/test.jpg',
        bucket: 'test-bucket',
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPresignedResponse,
        })
        .mockResolvedValueOnce({
          ok: false,
        });

      await expect(
        PresignedUploader.uploadWithPresignedUrl(file, endpoint)
      ).rejects.toThrow('Failed to upload file to S3');
    });

    it('should report error status in progress callback on failure', async () => {
      const file = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      const endpoint = '/api/v1/photos/upload';
      const progressCallback = jest.fn();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
      });

      await expect(
        PresignedUploader.uploadWithPresignedUrl(file, endpoint, progressCallback)
      ).rejects.toThrow();

      // エラー状態が報告されたことを確認
      const errorCall = progressCallback.mock.calls.find(
        (call) => call[0].status === 'error'
      );
      expect(errorCall).toBeDefined();
      expect(errorCall![0].error).toBeDefined();
    });
  });

  describe('uploadMultipleWithPresignedUrl', () => {
    it('should upload multiple files successfully', async () => {
      const files = [
        new File(['content1'], 'file1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'file2.jpg', { type: 'image/jpeg' }),
        new File(['content3'], 'file3.jpg', { type: 'image/jpeg' }),
      ];
      const endpoint = '/api/v1/photos/upload';

      // モックレスポンス
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ presignedUrl: 'url1', key: 'key1', bucket: 'bucket' }),
        })
        .mockResolvedValueOnce({ ok: true })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ presignedUrl: 'url2', key: 'key2', bucket: 'bucket' }),
        })
        .mockResolvedValueOnce({ ok: true })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ presignedUrl: 'url3', key: 'key3', bucket: 'bucket' }),
        })
        .mockResolvedValueOnce({ ok: true });

      const results = await PresignedUploader.uploadMultipleWithPresignedUrl(
        files,
        endpoint
      );

      expect(results).toHaveLength(3);
      expect(results[0].key).toBe('key1');
      expect(results[1].key).toBe('key2');
      expect(results[2].key).toBe('key3');
    });

    it('should call progress callback for each file', async () => {
      const files = [
        new File(['content1'], 'file1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'file2.jpg', { type: 'image/jpeg' }),
      ];
      const endpoint = '/api/v1/photos/upload';
      const progressCallback = jest.fn();

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ presignedUrl: 'url1', key: 'key1', bucket: 'bucket' }),
        })
        .mockResolvedValueOnce({ ok: true })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ presignedUrl: 'url2', key: 'key2', bucket: 'bucket' }),
        })
        .mockResolvedValueOnce({ ok: true });

      await PresignedUploader.uploadMultipleWithPresignedUrl(
        files,
        endpoint,
        progressCallback
      );

      // 各ファイルの進捗が報告されたことを確認
      expect(progressCallback).toHaveBeenCalledWith('file1.jpg', expect.any(Object));
      expect(progressCallback).toHaveBeenCalledWith('file2.jpg', expect.any(Object));
    });

    it('should respect maxConcurrent parameter', async () => {
      const files = Array.from({ length: 5 }, (_, i) =>
        new File([`content${i}`], `file${i}.jpg`, { type: 'image/jpeg' })
      );
      const endpoint = '/api/v1/photos/upload';

      // すべてのfetchコールをモック
      for (let i = 0; i < 10; i++) {
        (global.fetch as jest.Mock).mockResolvedValueOnce(
          i % 2 === 0
            ? {
                ok: true,
                json: async () => ({
                  presignedUrl: `url${i}`,
                  key: `key${i}`,
                  bucket: 'bucket',
                }),
              }
            : { ok: true }
        );
      }

      await PresignedUploader.uploadMultipleWithPresignedUrl(
        files,
        endpoint,
        undefined,
        2 // 最大2並列
      );

      // fetchが正しい回数呼ばれたことを確認（各ファイルにつき2回）
      expect(global.fetch).toHaveBeenCalledTimes(10);
    });
  });
});
