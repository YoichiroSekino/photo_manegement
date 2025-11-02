/**
 * エクスポートウィザードコンポーネント
 */

'use client';

import { useState } from 'react';
import { Photo } from '@/types/photo';

interface ExportWizardProps {
  onClose: () => void;
  onExport: (selectedPhotoIds: number[], options: ExportOptions) => Promise<void>;
}

export interface ExportOptions {
  includeXml: boolean;
  includeDtd: boolean;
  includeXsl: boolean;
  zipFilename: string;
}

enum WizardStep {
  SELECT_PHOTOS = 1,
  CONFIGURE = 2,
  EXPORT = 3,
}

export function ExportWizard({ onClose, onExport }: ExportWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>(WizardStep.SELECT_PHOTOS);
  const [selectedPhotoIds, setSelectedPhotoIds] = useState<number[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [options, setOptions] = useState<ExportOptions>({
    includeXml: true,
    includeDtd: true,
    includeXsl: true,
    zipFilename: `export_${new Date().toISOString().split('T')[0]}.zip`,
  });

  const handleSelectAll = () => {
    if (selectedPhotoIds.length === photos.length) {
      setSelectedPhotoIds([]);
    } else {
      setSelectedPhotoIds(photos.map((p) => p.id));
    }
  };

  const handleTogglePhoto = (photoId: number) => {
    setSelectedPhotoIds((prev) =>
      prev.includes(photoId)
        ? prev.filter((id) => id !== photoId)
        : [...prev, photoId]
    );
  };

  const handleNext = () => {
    setCurrentStep((prev) => Math.min(prev + 1, WizardStep.EXPORT) as WizardStep);
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, WizardStep.SELECT_PHOTOS) as WizardStep);
  };

  const handleExport = async () => {
    setIsLoading(true);
    setExportProgress(0);

    try {
      // シミュレーション用の進捗更新
      const progressInterval = setInterval(() => {
        setExportProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      await onExport(selectedPhotoIds, options);

      clearInterval(progressInterval);
      setExportProgress(100);

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Export error:', error);
      setExportProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* ヘッダー */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">電子納品パッケージ作成</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* ステップインジケーター */}
          <div className="mt-4 flex items-center justify-between">
            {[
              { step: WizardStep.SELECT_PHOTOS, label: '写真選択' },
              { step: WizardStep.CONFIGURE, label: '設定' },
              { step: WizardStep.EXPORT, label: 'エクスポート' },
            ].map(({ step, label }, index) => (
              <div key={step} className="flex items-center flex-1">
                <div className={`flex items-center ${index > 0 ? 'w-full' : ''}`}>
                  {index > 0 && (
                    <div
                      className={`flex-1 h-1 mx-2 ${
                        currentStep > step - 1 ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    />
                  )}
                  <div
                    className={`flex items-center justify-center w-8 h-8 rounded-full ${
                      currentStep >= step
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}
                  >
                    {step}
                  </div>
                  <span
                    className={`ml-2 text-sm font-medium ${
                      currentStep >= step ? 'text-blue-600' : 'text-gray-500'
                    }`}
                  >
                    {label}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* コンテンツ */}
        <div className="px-6 py-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {currentStep === WizardStep.SELECT_PHOTOS && (
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold">エクスポートする写真を選択</h3>
                <button
                  onClick={handleSelectAll}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {selectedPhotoIds.length === photos.length ? '全て解除' : '全て選択'}
                </button>
              </div>

              {photos.length === 0 ? (
                <p className="text-gray-500 text-center py-8">写真がありません</p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {photos.map((photo) => (
                    <div
                      key={photo.id}
                      onClick={() => handleTogglePhoto(photo.id)}
                      className={`relative border-2 rounded-lg p-2 cursor-pointer transition-colors ${
                        selectedPhotoIds.includes(photo.id)
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="aspect-video bg-gray-100 rounded mb-2 flex items-center justify-center">
                        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <p className="text-xs font-medium truncate">{photo.file_name}</p>
                      {selectedPhotoIds.includes(photo.id) && (
                        <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full p-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {currentStep === WizardStep.CONFIGURE && (
            <div>
              <h3 className="text-lg font-semibold mb-4">エクスポート設定</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ファイル名
                  </label>
                  <input
                    type="text"
                    value={options.zipFilename}
                    onChange={(e) => setOptions({ ...options, zipFilename: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    含めるファイル
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={options.includeXml}
                        onChange={(e) => setOptions({ ...options, includeXml: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">PHOTO.XML</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={options.includeDtd}
                        onChange={(e) => setOptions({ ...options, includeDtd: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">PHOTO05.DTD</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={options.includeXsl}
                        onChange={(e) => setOptions({ ...options, includeXsl: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">PHOTO05.XSL（オプション）</span>
                    </label>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">選択された写真</h4>
                  <p className="text-sm text-blue-700">{selectedPhotoIds.length}件</p>
                </div>
              </div>
            </div>
          )}

          {currentStep === WizardStep.EXPORT && (
            <div className="text-center py-8">
              {exportProgress < 100 ? (
                <>
                  <div className="mb-4">
                    <svg
                      className="animate-spin mx-auto h-12 w-12 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">エクスポート中...</h3>
                  <div className="max-w-md mx-auto">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${exportProgress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{exportProgress}%</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-4">
                    <svg
                      className="mx-auto h-12 w-12 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-green-900">エクスポート完了！</h3>
                  <p className="text-sm text-gray-600 mt-2">
                    ダウンロードが開始されます...
                  </p>
                </>
              )}
            </div>
          )}
        </div>

        {/* フッター */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            キャンセル
          </button>
          <div className="flex items-center space-x-3">
            {currentStep > WizardStep.SELECT_PHOTOS && currentStep < WizardStep.EXPORT && (
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                戻る
              </button>
            )}
            {currentStep < WizardStep.EXPORT && (
              <button
                onClick={currentStep === WizardStep.CONFIGURE ? handleExport : handleNext}
                disabled={currentStep === WizardStep.SELECT_PHOTOS && selectedPhotoIds.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {currentStep === WizardStep.CONFIGURE ? 'エクスポート' : '次へ'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
