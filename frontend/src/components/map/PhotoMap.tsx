/**
 * 地図ベース写真表示コンポーネント
 * 位置情報付き写真を地図上にマーカーで表示
 */

'use client';

import { useState } from 'react';
import { Photo } from '@/types/photo';

interface PhotoMapProps {
  photos: Photo[];
  onPhotoSelect?: (photoId: string) => void;
}

interface MapMarker {
  id: string;
  latitude: number;
  longitude: number;
  photo: Photo;
}

export function PhotoMap({ photos, onPhotoSelect }: PhotoMapProps) {
  const [selectedMarker, setSelectedMarker] = useState<string | null>(null);

  // 位置情報がある写真のみをフィルター
  const photosWithLocation = photos.filter(photo => photo.location);

  // マーカーデータを作成
  const markers: MapMarker[] = photosWithLocation.map(photo => ({
    id: photo.id,
    latitude: photo.location!.latitude,
    longitude: photo.location!.longitude,
    photo,
  }));

  // 地図の中心を計算（全マーカーの平均位置）
  const center = markers.length > 0
    ? {
        lat: markers.reduce((sum, m) => sum + m.latitude, 0) / markers.length,
        lng: markers.reduce((sum, m) => sum + m.longitude, 0) / markers.length,
      }
    : { lat: 35.6812, lng: 139.7671 }; // デフォルト: 東京

  const handleMarkerClick = (markerId: string) => {
    setSelectedMarker(markerId);
    if (onPhotoSelect) {
      onPhotoSelect(markerId);
    }
  };

  if (markers.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">位置情報付きの写真がありません</h3>
        <p className="mt-1 text-sm text-gray-500">
          GPS情報を含む写真をアップロードすると、地図上に表示されます。
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* 簡易マップビュー（静的画像版） */}
      <div className="relative h-96 bg-gray-100">
        {/* 地図プレースホルダー */}
        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <svg className="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <p className="text-sm">地図表示（{markers.length}件の写真）</p>
            <p className="text-xs mt-1">中心: {center.lat.toFixed(4)}, {center.lng.toFixed(4)}</p>
          </div>
        </div>

        {/* マーカー一覧（簡易表示） */}
        <div className="absolute bottom-0 left-0 right-0 bg-white bg-opacity-95 p-2 max-h-32 overflow-y-auto">
          <div className="flex flex-wrap gap-1">
            {markers.map((marker) => (
              <button
                key={marker.id}
                onClick={() => handleMarkerClick(marker.id)}
                className={`px-2 py-1 text-xs rounded ${
                  selectedMarker === marker.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                📍 {marker.photo.fileName}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 選択された写真の詳細 */}
      {selectedMarker && (
        <div className="border-t p-4">
          {(() => {
            const selected = markers.find(m => m.id === selectedMarker);
            if (!selected) return null;

            return (
              <div className="flex items-start space-x-4">
                <img
                  src={selected.photo.s3Url}
                  alt={selected.photo.title || selected.photo.fileName}
                  className="w-24 h-24 object-cover rounded"
                />
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">
                    {selected.photo.title || selected.photo.fileName}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    📍 {selected.photo.location?.address ||
                       `${selected.latitude.toFixed(4)}, ${selected.longitude.toFixed(4)}`}
                  </p>
                  {selected.photo.shootingDate && (
                    <p className="text-xs text-gray-500 mt-1">
                      📅 {new Date(selected.photo.shootingDate).toLocaleString('ja-JP')}
                    </p>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* 統計情報 */}
      <div className="border-t bg-gray-50 px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            位置情報付き写真: {markers.length}件
          </span>
          <span className="text-gray-500">
            範囲: {Math.min(...markers.map(m => m.latitude)).toFixed(4)} ~ {Math.max(...markers.map(m => m.latitude)).toFixed(4)}
          </span>
        </div>
      </div>
    </div>
  );
}
