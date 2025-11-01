'use client';

import { useState } from 'react';
import { PhotoGrid } from '@/components/photos/PhotoGrid';
import { Photo } from '@/types/photo';

export default function PhotosPage() {
  // TODO: 実際のデータはZustandストアまたはReact Queryから取得
  const [photos] = useState<Photo[]>([]);

  const handlePhotoSelect = (id: string) => {
    console.log('Selected photo:', id);
    // TODO: 写真詳細ページへ遷移またはモーダル表示
  };

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">写真一覧</h1>
            <p className="text-gray-600">
              アップロードされた工事写真を閲覧・管理できます
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">
              {photos.length} 件の写真
            </span>
          </div>
        </div>

        <PhotoGrid photos={photos} onPhotoSelect={handlePhotoSelect} />
      </div>
    </main>
  );
}
