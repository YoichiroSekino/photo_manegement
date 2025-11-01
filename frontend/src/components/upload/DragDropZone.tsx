import { FC, useState, useCallback, DragEvent, ChangeEvent } from 'react';

interface DragDropZoneProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
}

/**
 * ドラッグ&ドロップゾーンコンポーネント
 *
 * @param onFilesSelected - ファイル選択時のコールバック
 * @param maxFiles - 最大ファイル数（デフォルト: 無制限）
 */
export const DragDropZone: FC<DragDropZoneProps> = ({
  onFilesSelected,
  maxFiles,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragEnter = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      const files = Array.from(e.dataTransfer.files);
      const limitedFiles = maxFiles ? files.slice(0, maxFiles) : files;
      onFilesSelected(limitedFiles);
    },
    [onFilesSelected, maxFiles]
  );

  const handleFileInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files ? Array.from(e.target.files) : [];
      const limitedFiles = maxFiles ? files.slice(0, maxFiles) : files;
      onFilesSelected(limitedFiles);
    },
    [onFilesSelected, maxFiles]
  );

  return (
    <div
      data-testid="drop-zone"
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative
        flex
        flex-col
        items-center
        justify-center
        w-full
        h-64
        border-2
        border-dashed
        rounded-lg
        transition-colors
        cursor-pointer
        ${isDragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'}
        hover:border-primary-400
        hover:bg-primary-25
      `}
    >
      <input
        data-testid="file-input"
        type="file"
        multiple
        accept="image/jpeg,image/tiff"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />

      <div className="flex flex-col items-center text-center pointer-events-none">
        <svg
          className="w-16 h-16 mb-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        <p className="mb-2 text-sm text-gray-700">
          <span className="font-semibold">ここにファイルをドラッグ&ドロップ</span>
        </p>
        <p className="text-xs text-gray-500">または クリックしてファイルを選択</p>
        <p className="mt-2 text-xs text-gray-400">JPEG, TIFF形式のみ対応</p>
        {maxFiles && (
          <p className="mt-1 text-xs text-gray-400">最大 {maxFiles} ファイルまで</p>
        )}
      </div>
    </div>
  );
};
