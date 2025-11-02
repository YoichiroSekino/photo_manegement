import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import { QueryProvider } from '@/providers/QueryProvider';
import { NotificationToast } from '@/components/common/NotificationToast';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '工事写真自動整理システム',
  description:
    '建設現場で撮影される大量の工事写真をAIで自動的に整理・分類し、国土交通省の「デジタル写真管理情報基準」に準拠した形で管理するシステム',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <ErrorBoundary>
          <QueryProvider>
            <AuthProvider>
              {children}
              <NotificationToast />
            </AuthProvider>
          </QueryProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
