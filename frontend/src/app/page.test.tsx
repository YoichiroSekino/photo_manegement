import { render, screen } from '@testing-library/react';
import Home from './page';

describe('Home Page', () => {
  it('ページがレンダリングされる', () => {
    render(<Home />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('アプリケーションタイトルが表示される', () => {
    render(<Home />);
    expect(screen.getByText(/工事写真自動整理システム/i)).toBeInTheDocument();
  });

  it('説明文が表示される', () => {
    render(<Home />);
    expect(
      screen.getByText(/建設現場で撮影される大量の工事写真を/i)
    ).toBeInTheDocument();
  });
});
