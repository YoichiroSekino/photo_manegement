import { render, screen } from '@testing-library/react';
import Home from './page';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/',
}));

const renderWithAuth = (ui: React.ReactElement) => {
  return render(<AuthProvider>{ui}</AuthProvider>);
};

describe('Home Page', () => {
  beforeEach(() => {
    // Mock fetch for auth check
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: async () => ({}),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('ページがレンダリングされる', async () => {
    renderWithAuth(<Home />);
    // Wait for loading to finish
    await screen.findByRole('main');
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('アプリケーションタイトルが表示される', async () => {
    renderWithAuth(<Home />);
    await screen.findByRole('main');
    expect(screen.getByText(/工事写真自動整理システム/i)).toBeInTheDocument();
  });

  it('説明文が表示される', async () => {
    renderWithAuth(<Home />);
    await screen.findByRole('main');
    expect(
      screen.getByText(/建設現場で撮影される大量の工事写真を/i)
    ).toBeInTheDocument();
  });
});
