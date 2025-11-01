import { render, screen, fireEvent } from '@testing-library/react';
import { DragDropZone } from '../DragDropZone';

describe('DragDropZone', () => {
  it('レンダリングされる', () => {
    render(<DragDropZone onFilesSelected={jest.fn()} />);
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
  });

  it('ドロップゾーンにテキストが表示される', () => {
    render(<DragDropZone onFilesSelected={jest.fn()} />);
    expect(
      screen.getByText(/ここにファイルをドラッグ&ドロップ/i)
    ).toBeInTheDocument();
  });

  it('JPEGファイルを受け入れる', () => {
    const mockOnFilesSelected = jest.fn();
    render(<DragDropZone onFilesSelected={mockOnFilesSelected} />);

    const file = new File(['dummy content'], 'test.jpg', {
      type: 'image/jpeg',
    });
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;

    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    expect(mockOnFilesSelected).toHaveBeenCalledWith([file]);
  });

  it('複数ファイルを受け入れる', () => {
    const mockOnFilesSelected = jest.fn();
    render(<DragDropZone onFilesSelected={mockOnFilesSelected} />);

    const files = [
      new File(['content1'], 'test1.jpg', { type: 'image/jpeg' }),
      new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      new File(['content3'], 'test3.jpg', { type: 'image/jpeg' }),
    ];

    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;

    Object.defineProperty(fileInput, 'files', {
      value: files,
      writable: false,
    });

    fireEvent.change(fileInput);

    expect(mockOnFilesSelected).toHaveBeenCalledWith(files);
  });

  it('JPEGとTIFF形式のみ受け入れる', () => {
    render(<DragDropZone onFilesSelected={jest.fn()} />);
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;

    expect(fileInput.accept).toBe('image/jpeg,image/tiff');
  });

  it('ドラッグオーバー時にスタイルが変わる', () => {
    render(<DragDropZone onFilesSelected={jest.fn()} />);
    const dropZone = screen.getByTestId('drop-zone');

    fireEvent.dragEnter(dropZone);
    expect(dropZone.className).toContain('border-primary-500');

    fireEvent.dragLeave(dropZone);
    expect(dropZone.className).not.toContain('border-primary-500');
  });
});
