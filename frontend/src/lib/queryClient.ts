/**
 * React Query設定
 */

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // データが古くなるまでの時間（5分）
      staleTime: 5 * 60 * 1000,
      // キャッシュが保持される時間（10分）
      gcTime: 10 * 60 * 1000,
      // ウィンドウフォーカス時の自動再取得を無効化
      refetchOnWindowFocus: false,
      // リトライ回数
      retry: 1,
      // リトライ遅延（指数バックオフ）
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // リトライ回数
      retry: 1,
    },
  },
});
