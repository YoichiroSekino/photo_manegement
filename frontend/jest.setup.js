// Jest setup file
import '@testing-library/jest-dom';

// グローバルモック設定
global.fetch = jest.fn();

// Next.js router モック
jest.mock('next/router', () => require('next-router-mock'));

// Next.js navigation モック（App Router用）
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
  usePathname: jest.fn(() => '/'),
  useSearchParams: jest.fn(() => new URLSearchParams()),
}));
