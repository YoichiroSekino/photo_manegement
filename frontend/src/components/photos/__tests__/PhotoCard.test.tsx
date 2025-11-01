import { render, screen, fireEvent } from '@testing-library/react';
import { PhotoCard } from '../PhotoCard';
import { Photo } from '@/types/photo';

const mockPhoto: Photo = {
  id: '1',
  fileName: 'test.jpg',
  fileSize: 1024000,
  mimeType: 'image/jpeg',
  thumbnailUrl: 'https://example.com/thumb.jpg',
  title: 'テスト写真',
  description: 'これはテスト用の写真です',
  shootingDate: '2024-03-15',
  createdAt: '2024-03-15T10:00:00Z',
  updatedAt: '2024-03-15T10:00:00Z',
};

describe('PhotoCard', () => {
  it('レンダリングされる', () => {
    render(<PhotoCard photo={mockPhoto} />);
    expect(screen.getByTestId('photo-card')).toBeInTheDocument();
  });

  it('写真のタイトルが表示される', () => {
    render(<PhotoCard photo={mockPhoto} />);
    expect(screen.getByText('テスト写真')).toBeInTheDocument();
  });

  it('ファイル名がタイトルとして表示される（タイトルがない場合）', () => {
    const photoWithoutTitle = { ...mockPhoto, title: undefined };
    render(<PhotoCard photo={photoWithoutTitle} />);
    expect(screen.getByText('test.jpg')).toBeInTheDocument();
  });

  it('撮影日が表示される', () => {
    render(<PhotoCard photo={mockPhoto} />);
    expect(screen.getByText(/2024-03-15/)).toBeInTheDocument();
  });

  it('クリック時にonSelectが呼ばれる', () => {
    const mockOnSelect = jest.fn();
    render(<PhotoCard photo={mockPhoto} onSelect={mockOnSelect} />);

    const card = screen.getByTestId('photo-card');
    fireEvent.click(card);

    expect(mockOnSelect).toHaveBeenCalledWith('1');
  });

  it('サムネイルURLが設定されている', () => {
    render(<PhotoCard photo={mockPhoto} />);
    const img = screen.getByRole('img') as HTMLImageElement;
    expect(img.src).toContain('thumb.jpg');
  });
});
