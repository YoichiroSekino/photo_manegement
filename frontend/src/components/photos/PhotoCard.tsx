import { FC, useCallback } from 'react';
import { Photo } from '@/types/photo';
import Image from 'next/image';

interface PhotoCardProps {
  photo: Photo;
  onSelect?: (id: string) => void;
}

/**
 * 写真カードコンポーネント
 *
 * @param photo - 表示する写真データ
 * @param onSelect - 選択時のコールバック
 */
export const PhotoCard: FC<PhotoCardProps> = ({ photo, onSelect }) => {
  const handleClick = useCallback(() => {
    onSelect?.(photo.id);
  }, [photo.id, onSelect]);

  // サムネイルURLを決定（thumbnailUrl > s3_url）
  const imageUrl = photo.thumbnailUrl || photo.s3Url;

  return (
    <div
      data-testid="photo-card"
      onClick={handleClick}
      className="group relative bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
    >
      {/* サムネイル画像 */}
      <div className="relative aspect-video bg-gray-100">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={photo.title || photo.fileName}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-200"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <svg
              className="w-16 h-16 text-gray-300"
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
          </div>
        )}
      </div>

      {/* 写真情報 */}
      <div className="p-4">
        <h3 className="text-sm font-semibold text-gray-900 line-clamp-1 mb-1">
          {photo.title || photo.fileName}
        </h3>

        {photo.shootingDate && (
          <p className="text-xs text-gray-500 mb-2">{photo.shootingDate}</p>
        )}

        {photo.description && (
          <p className="text-xs text-gray-600 line-clamp-2">{photo.description}</p>
        )}

        {photo.category && (
          <div className="mt-2">
            <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded">
              {photo.category.photoType}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
