'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { ExportWizard, ExportOptions } from '@/components/export/ExportWizard';
import { PhotoAlbumDialog, AlbumOptions } from '@/components/export/PhotoAlbumDialog';

export default function ExportPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [showExportWizard, setShowExportWizard] = useState(false);
  const [showPhotoAlbum, setShowPhotoAlbum] = useState(false);

  // 認証チェック
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  const handleExport = async (selectedPhotoIds: string[], options: ExportOptions) => {
    const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const accessToken = localStorage.getItem('access_token');

    try {
      const response = await fetch(`${apiEndpoint}/api/v1/export/package`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({
          photo_ids: selectedPhotoIds.map(id => parseInt(id, 10)),  // Convert string IDs to numbers for API
          include_xml: options.includeXml,
          include_dtd: options.includeDtd,
          include_xsl: options.includeXsl,
        }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = options.zipFilename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
      throw error;
    }
  };

  const handleGenerateAlbum = async (options: AlbumOptions) => {
    const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const accessToken = localStorage.getItem('access_token');

    try {
      const response = await fetch(`${apiEndpoint}/api/v1/photo-album/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({
          layout: options.layout,
          template: options.template,
          cover_info: options.coverInfo,
          add_page_numbers: options.addPageNumbers,
          header_text: options.headerText,
          footer_text: options.footerText,
        }),
      });

      if (!response.ok) {
        throw new Error('Album generation failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `photo_album_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Album generation error:', error);
      throw error;
    }
  };

  return (
    <main className="flex min-h-screen flex-col p-8">
      <div className="max-w-5xl mx-auto w-full">
        <h1 className="text-3xl font-bold mb-2">エクスポート・出力</h1>
        <p className="text-gray-600 mb-8">
          電子納品パッケージの作成や工事写真帳のPDF生成を行います。
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 電子納品パッケージ */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0">
                <svg
                  className="w-12 h-12 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-bold text-gray-900 mb-2">電子納品パッケージ</h2>
                <p className="text-sm text-gray-600 mb-4">
                  国土交通省「デジタル写真管理情報基準」に準拠した電子納品用ZIPパッケージを作成します。
                </p>
                <ul className="text-sm text-gray-600 space-y-1 mb-4">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    PHOTO.XML自動生成
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    ファイル名自動リネーム（Pnnnnnnn.JPG）
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    フォルダ構造自動生成（PHOTO/PIC/, DRA/）
                  </li>
                </ul>
                <button
                  onClick={() => setShowExportWizard(true)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  パッケージ作成
                </button>
              </div>
            </div>
          </div>

          {/* 工事写真帳 */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0">
                <svg
                  className="w-12 h-12 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-bold text-gray-900 mb-2">工事写真帳（PDF）</h2>
                <p className="text-sm text-gray-600 mb-4">
                  見栄えの良いPDF形式の工事写真帳を自動生成します。レイアウトやテンプレートを選択できます。
                </p>
                <ul className="text-sm text-gray-600 space-y-1 mb-4">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    3種類のレイアウト選択
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    表紙自動生成
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    カスタマイズ可能
                  </li>
                </ul>
                <button
                  onClick={() => setShowPhotoAlbum(true)}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors"
                >
                  写真帳生成
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 使い方ガイド */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">使い方</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-900 mb-2">電子納品パッケージ</h4>
              <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                <li>エクスポートする写真を選択</li>
                <li>含めるファイル（XML, DTD, XSL）を設定</li>
                <li>ZIPファイル名を指定</li>
                <li>エクスポート実行</li>
              </ol>
            </div>
            <div>
              <h4 className="font-medium text-blue-900 mb-2">工事写真帳</h4>
              <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                <li>レイアウトとテンプレートを選択</li>
                <li>表紙情報（工事名、施工業者等）を入力</li>
                <li>カスタマイズオプションを設定</li>
                <li>PDF生成</li>
              </ol>
            </div>
          </div>
        </div>
      </div>

      {/* ダイアログ */}
      {showExportWizard && (
        <ExportWizard
          onClose={() => setShowExportWizard(false)}
          onExport={handleExport}
        />
      )}

      {showPhotoAlbum && (
        <PhotoAlbumDialog
          onClose={() => setShowPhotoAlbum(false)}
          onGenerate={handleGenerateAlbum}
        />
      )}
    </main>
  );
}
