/**
 * React Query設定
 */

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // データが古くなるまでの時間（写真データは頻繁に変わらないので10分）
      staleTime: 10 * 60 * 1000,
      // キャッシュが保持される時間（30分）
      gcTime: 30 * 60 * 1000,
      // ウィンドウフォーカス時の自動再取得を無効化（画像データは重いため）
      refetchOnWindowFocus: false,
      // マウント時の自動再取得を無効化（キャッシュを優先）
      refetchOnMount: false,
      // リトライ回数（画像データは失敗しやすいので2回）
      retry: 2,
      // リトライ遅延（指数バックオフ）
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // リトライ回数
      retry: 1,
    },
  },
});
