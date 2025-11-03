import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';
import { apiClient } from '@/lib/apiClient';

// Mock apiClient
jest.mock('@/lib/apiClient', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state initially', () => {
    mockedApiClient.get.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<Dashboard />);

    expect(screen.getByText('読み込み中...')).toBeInTheDocument();
  });

  it('displays dashboard stats and recent photos', async () => {
    const mockStats = {
      total_photos: 100,
      today_uploads: 5,
      this_week_uploads: 20,
      duplicates_count: 3,
      quality_issues_count: 2,
      category_distribution: {
        '施工状況写真': 50,
        '安全管理写真': 30,
      },
    };

    const mockPhotos = [
      {
        id: 1,
        file_name: 'P0000001.JPG',
        s3_key: 'photos/P0000001.JPG',
        title: 'Test Photo 1',
        major_category: '施工状況写真',
        shooting_date: '2024-01-01',
        quality_score: 85,
        created_at: '2024-01-01T00:00:00Z',
      },
    ];

    mockedApiClient.get
      .mockResolvedValueOnce(mockStats)
      .mockResolvedValueOnce(mockPhotos);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('ダッシュボード')).toBeInTheDocument();
    });

    // Check stats cards
    expect(screen.getByText('総写真数')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('今日のアップロード')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();

    // Check category distribution
    expect(screen.getByText('カテゴリ別写真数')).toBeInTheDocument();
    expect(screen.getAllByText('施工状況写真').length).toBeGreaterThan(0);
    expect(screen.getByText('50')).toBeInTheDocument();

    // Check recent photos
    expect(screen.getByText('最近アップロードした写真')).toBeInTheDocument();
    expect(screen.getByText('Test Photo 1')).toBeInTheDocument();
  });

  it('shows quality issues alert when quality_issues_count > 0', async () => {
    const mockStats = {
      total_photos: 100,
      today_uploads: 5,
      this_week_uploads: 20,
      duplicates_count: 3,
      quality_issues_count: 10,
      category_distribution: {},
    };

    mockedApiClient.get
      .mockResolvedValueOnce(mockStats)
      .mockResolvedValueOnce([]);

    render(<Dashboard />);

    await waitFor(
      () => {
        expect(screen.getByText(/枚の写真に品質の問題があります/)).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('handles API error gracefully', async () => {
    mockedApiClient.get.mockRejectedValueOnce(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('ダッシュボードデータの取得に失敗しました')).toBeInTheDocument();
    });
  });

  it('shows empty state for recent photos', async () => {
    const mockStats = {
      total_photos: 0,
      today_uploads: 0,
      this_week_uploads: 0,
      duplicates_count: 0,
      quality_issues_count: 0,
      category_distribution: {},
    };

    mockedApiClient.get
      .mockResolvedValueOnce(mockStats)
      .mockResolvedValueOnce([]);

    render(<Dashboard />);

    await waitFor(
      () => {
        expect(screen.getByText('まだ写真がアップロードされていません')).toBeInTheDocument();
        expect(screen.getAllByText('写真をアップロード').length).toBeGreaterThan(0);
      },
      { timeout: 3000 }
    );
  });
});
