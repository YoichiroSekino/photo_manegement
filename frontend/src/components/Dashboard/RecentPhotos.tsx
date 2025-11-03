import Link from 'next/link';
import Image from 'next/image';

interface Photo {
  id: number;
  file_name: string;
  s3_key: string;
  s3_url?: string;
  title: string | null;
  major_category: string | null;
  shooting_date: string | null;
  quality_score: number | null;
  created_at: string;
}

interface RecentPhotosProps {
  photos: Photo[];
}

export default function RecentPhotos({ photos }: RecentPhotosProps) {
  if (photos.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">最近アップロードした写真</h2>
        <p className="text-gray-500 text-center py-8">まだ写真がアップロードされていません</p>
        <div className="text-center">
          <Link
            href="/upload"
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            写真をアップロード
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">最近アップロードした写真</h2>
        <Link href="/photos" className="text-blue-600 hover:text-blue-800 text-sm">
          すべて見る →
        </Link>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {photos.map((photo) => (
          <div
            key={photo.id}
            className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
          >
            <div className="relative aspect-video bg-gray-200">
              {photo.s3_url ? (
                <Image
                  src={photo.s3_url}
                  alt={photo.title || photo.file_name}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <svg
                    className="w-12 h-12 text-gray-400"
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
            <div className="p-3">
              <p className="text-sm font-medium text-gray-900 truncate">
                {photo.title || photo.file_name}
              </p>
              {photo.major_category && (
                <p className="text-xs text-gray-500 mt-1">{photo.major_category}</p>
              )}
              {photo.quality_score !== null && (
                <div className="mt-2">
                  <div className="flex items-center">
                    <span className="text-xs text-gray-600">品質:</span>
                    <span
                      className={`ml-1 text-xs font-medium ${
                        photo.quality_score >= 70
                          ? 'text-green-600'
                          : photo.quality_score >= 50
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {photo.quality_score}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
