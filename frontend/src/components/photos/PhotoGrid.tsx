import { FC } from 'react';
import { Photo } from '@/types/photo';
import { PhotoCard } from './PhotoCard';

interface PhotoGridProps {
  photos: Photo[];
  onPhotoSelect?: (id: string) => void;
}

/**
 * 写真グリッドコンポーネント
 *
 * @param photos - 表示する写真の配列
 * @param onPhotoSelect - 写真選択時のコールバック
 */
export const PhotoGrid: FC<PhotoGridProps> = ({ photos, onPhotoSelect }) => {
  if (photos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-500">
        <svg
          className="w-24 h-24 mb-4 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="text-lg font-medium">写真がありません</p>
        <p className="text-sm mt-1">アップロードページから写真を追加してください</p>
      </div>
    );
  }

  return (
    <div
      data-testid="photo-grid"
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
    >
      {photos.map((photo) => (
        <PhotoCard key={photo.id} photo={photo} onSelect={onPhotoSelect} />
      ))}
    </div>
  );
};
