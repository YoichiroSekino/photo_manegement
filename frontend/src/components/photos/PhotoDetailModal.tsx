/**
 * 写真詳細モーダル
 * OCR結果、AI認識結果、メタデータを表示
 */

'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Photo } from '@/types/photo';
import { useProcessOCR, useClassifyPhoto } from '@/hooks/usePhotos';

interface PhotoDetailModalProps {
  photo: Photo;
  onClose: () => void;
}

export function PhotoDetailModal({ photo, onClose }: PhotoDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'ocr' | 'ai'>('info');
  const processOCR = useProcessOCR();
  const classifyPhoto = useClassifyPhoto();

  const handleProcessOCR = async () => {
    try {
      await processOCR.mutateAsync(Number(photo.id));
    } catch (error) {
      console.error('OCR processing failed:', error);
    }
  };

  const handleClassify = async () => {
    try {
      await classifyPhoto.mutateAsync(Number(photo.id));
    } catch (error) {
      console.error('AI classification failed:', error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-2 sm:p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative w-full max-w-4xl bg-white rounded-lg shadow-xl max-h-[95vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between border-b px-4 sm:px-6 py-3 sm:py-4 sticky top-0 bg-white z-10">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">写真詳細</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex flex-col lg:flex-row">
            {/* Image */}
            <div className="flex-shrink-0 bg-gray-100 p-4 sm:p-6 lg:w-1/2">
              <div className="relative w-full aspect-video">
                {photo.s3Url && (
                  <Image
                    src={photo.s3Url}
                    alt={photo.title || photo.fileName}
                    fill
                    className="object-contain rounded-lg"
                    sizes="50vw"
                    priority
                  />
                )}
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p>{photo.fileName}</p>
                <p>{(photo.fileSize / 1024 / 1024).toFixed(2)} MB</p>
                {photo.metadata && (
                  <p>{photo.metadata.width} × {photo.metadata.height} px</p>
                )}
              </div>
            </div>

            {/* Details */}
            <div className="flex-1 p-4 sm:p-6">
              {/* Tabs */}
              <div className="border-b mb-4">
                <nav className="-mb-px flex space-x-4 sm:space-x-8 overflow-x-auto">
                  <button
                    onClick={() => setActiveTab('info')}
                    className={`whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium ${
                      activeTab === 'info'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    基本情報
                  </button>
                  <button
                    onClick={() => setActiveTab('ocr')}
                    className={`whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium ${
                      activeTab === 'ocr'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    OCR結果
                  </button>
                  <button
                    onClick={() => setActiveTab('ai')}
                    className={`whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium ${
                      activeTab === 'ai'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    AI認識
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="overflow-y-auto max-h-64 sm:max-h-96">
                {activeTab === 'info' && (
                  <div className="space-y-4">
                    {photo.title && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">タイトル</label>
                        <p className="mt-1 text-sm text-gray-900">{photo.title}</p>
                      </div>
                    )}

                    {photo.description && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">説明</label>
                        <p className="mt-1 text-sm text-gray-900">{photo.description}</p>
                      </div>
                    )}

                    {photo.shootingDate && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">撮影日時</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {new Date(photo.shootingDate).toLocaleString('ja-JP')}
                        </p>
                      </div>
                    )}

                    {photo.location && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">位置情報</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {photo.location.address || `${photo.location.latitude}, ${photo.location.longitude}`}
                        </p>
                      </div>
                    )}

                    {photo.category && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">カテゴリ</label>
                        <div className="mt-1 flex flex-wrap gap-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {photo.category.majorCategory}
                          </span>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {photo.category.photoType}
                          </span>
                        </div>
                      </div>
                    )}

                    {photo.tags && photo.tags.length > 0 && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">タグ</label>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {photo.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'ocr' && (
                  <div className="space-y-4">
                    {photo.metadata?.blackboard ? (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-medium text-gray-700">黒板テキスト</label>
                          <span className="text-xs text-gray-500">
                            信頼度: {(photo.metadata.blackboard.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <p className="text-sm text-gray-900 whitespace-pre-wrap">
                            {photo.metadata.blackboard.text}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <p className="mt-2 text-sm text-gray-600">OCR処理が実行されていません</p>
                        <button
                          onClick={handleProcessOCR}
                          disabled={processOCR.isPending}
                          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                        >
                          {processOCR.isPending ? '処理中...' : 'OCR処理を実行'}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'ai' && (
                  <div className="space-y-4">
                    {photo.tags && photo.tags.length > 0 ? (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          検出されたラベル
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {photo.tags.map((label, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                            >
                              {label}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <p className="mt-2 text-sm text-gray-600">AI分類が実行されていません</p>
                        <button
                          onClick={handleClassify}
                          disabled={classifyPhoto.isPending}
                          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400"
                        >
                          {classifyPhoto.isPending ? '処理中...' : 'AI分類を実行'}
                        </button>
                      </div>
                    )}

                    {photo.metadata?.quality && (
                      <div className="mt-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          画質評価
                        </label>
                        <div className="space-y-2">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-600">シャープネス</span>
                              <span className="font-medium">{(photo.metadata.quality.sharpness * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-green-600 h-2 rounded-full"
                                style={{ width: `${photo.metadata.quality.sharpness * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t px-4 sm:px-6 py-3 sm:py-4 flex justify-end space-x-3 sticky bottom-0 bg-white">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
