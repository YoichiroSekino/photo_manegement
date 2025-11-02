/**
 * 工事写真帳生成ダイアログ
 */

'use client';

import { useState } from 'react';

interface PhotoAlbumDialogProps {
  onClose: () => void;
  onGenerate: (options: AlbumOptions) => Promise<void>;
}

export type LayoutType = 'standard' | 'compact' | 'detailed';

export interface AlbumOptions {
  layout: LayoutType;
  template: string;
  coverInfo: {
    projectName: string;
    contractor: string;
    period: string;
    client: string;
  };
  addPageNumbers: boolean;
  headerText?: string;
  footerText?: string;
}

const LAYOUTS = [
  { id: 'standard' as LayoutType, name: '標準レイアウト', description: '1ページ2枚表示' },
  { id: 'compact' as LayoutType, name: 'コンパクト', description: '1ページ4枚表示' },
  { id: 'detailed' as LayoutType, name: '詳細', description: '1ページ1枚+説明' },
];

const TEMPLATES = [
  { id: 'mlit', name: '国土交通省標準', description: '国交省様式準拠' },
  { id: 'municipal', name: '地方自治体', description: '自治体向け様式' },
  { id: 'custom', name: 'カスタム', description: '独自様式' },
];

export function PhotoAlbumDialog({ onClose, onGenerate }: PhotoAlbumDialogProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [options, setOptions] = useState<AlbumOptions>({
    layout: 'standard',
    template: 'mlit',
    coverInfo: {
      projectName: '',
      contractor: '',
      period: '',
      client: '',
    },
    addPageNumbers: true,
    headerText: '',
    footerText: '',
  });

  const handleGenerate = async () => {
    setIsGenerating(true);
    setProgress(0);

    try {
      // 進捗シミュレーション
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 300);

      await onGenerate(options);

      clearInterval(progressInterval);
      setProgress(100);

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Album generation error:', error);
      setProgress(0);
    } finally {
      setIsGenerating(false);
    }
  };

  const isFormValid = () => {
    return (
      options.coverInfo.projectName &&
      options.coverInfo.contractor &&
      options.coverInfo.period &&
      options.coverInfo.client
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        {/* ヘッダー */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">工事写真帳作成</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* コンテンツ */}
        <div className="px-6 py-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 180px)' }}>
          {!isGenerating ? (
            <div className="space-y-6">
              {/* レイアウト選択 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  レイアウト
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {LAYOUTS.map((layout) => (
                    <button
                      key={layout.id}
                      onClick={() => setOptions({ ...options, layout: layout.id })}
                      className={`p-4 border-2 rounded-lg text-left transition-colors ${
                        options.layout === layout.id
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <h4 className="font-medium text-sm mb-1">{layout.name}</h4>
                      <p className="text-xs text-gray-600">{layout.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* テンプレート選択 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  テンプレート
                </label>
                <div className="space-y-2">
                  {TEMPLATES.map((template) => (
                    <label key={template.id} className="flex items-start">
                      <input
                        type="radio"
                        name="template"
                        checked={options.template === template.id}
                        onChange={() => setOptions({ ...options, template: template.id })}
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <div className="ml-3">
                        <span className="text-sm font-medium text-gray-900">{template.name}</span>
                        <p className="text-xs text-gray-500">{template.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* 表紙情報 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  表紙情報
                </label>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">工事名称 *</label>
                    <input
                      type="text"
                      value={options.coverInfo.projectName}
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          coverInfo: { ...options.coverInfo, projectName: e.target.value },
                        })
                      }
                      placeholder="○○道路改良工事"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">施工業者 *</label>
                    <input
                      type="text"
                      value={options.coverInfo.contractor}
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          coverInfo: { ...options.coverInfo, contractor: e.target.value },
                        })
                      }
                      placeholder="株式会社○○建設"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">工期 *</label>
                    <input
                      type="text"
                      value={options.coverInfo.period}
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          coverInfo: { ...options.coverInfo, period: e.target.value },
                        })
                      }
                      placeholder="2024年4月〜2025年3月"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">発注者 *</label>
                    <input
                      type="text"
                      value={options.coverInfo.client}
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          coverInfo: { ...options.coverInfo, client: e.target.value },
                        })
                      }
                      placeholder="○○市役所"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* カスタマイズオプション */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  カスタマイズオプション
                </label>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={options.addPageNumbers}
                      onChange={(e) =>
                        setOptions({ ...options, addPageNumbers: e.target.checked })
                      }
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">ページ番号を追加</span>
                  </label>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">ヘッダーテキスト（オプション）</label>
                    <input
                      type="text"
                      value={options.headerText}
                      onChange={(e) => setOptions({ ...options, headerText: e.target.value })}
                      placeholder="工事写真帳"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">フッターテキスト（オプション）</label>
                    <input
                      type="text"
                      value={options.footerText}
                      onChange={(e) => setOptions({ ...options, footerText: e.target.value })}
                      placeholder="社外秘"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              {progress < 100 ? (
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
                  <h3 className="text-lg font-semibold mb-2">写真帳を生成中...</h3>
                  <div className="max-w-md mx-auto">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{progress}%</p>
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
                  <h3 className="text-lg font-semibold text-green-900">生成完了！</h3>
                  <p className="text-sm text-gray-600 mt-2">PDFのダウンロードが開始されます...</p>
                </>
              )}
            </div>
          )}
        </div>

        {/* フッター */}
        {!isGenerating && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              キャンセル
            </button>
            <button
              onClick={handleGenerate}
              disabled={!isFormValid()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              PDF生成
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
