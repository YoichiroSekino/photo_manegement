/**
 * API Client のテスト
 */

import {
  apiFetch,
  apiGet,
  apiPost,
  apiPut,
  apiPatch,
  apiDelete,
  ApiError,
} from '../apiClient';

// グローバルfetchのモック
global.fetch = jest.fn();

describe('ApiError', () => {
  it('should create an ApiError with correct properties', () => {
    const error = new ApiError(404, 'Not Found', { message: 'Resource not found' });

    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe('ApiError');
    expect(error.status).toBe(404);
    expect(error.statusText).toBe('Not Found');
    expect(error.data).toEqual({ message: 'Resource not found' });
    expect(error.message).toBe('API Error: 404 Not Found');
  });
});

describe('apiFetch', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // localStorage のモック
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  it('should make a successful GET request', async () => {
    const mockData = { id: 1, name: 'Test' };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const result = await apiFetch<typeof mockData>('/test');

    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('should include Authorization header when access token exists', async () => {
    const mockData = { id: 1 };
    (window.localStorage.getItem as jest.Mock).mockReturnValue('test-token');
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    await apiFetch('/test');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        }),
      })
    );
  });

  it('should handle 204 No Content response', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    const result = await apiFetch('/test');

    expect(result).toEqual({});
  });

  it('should throw ApiError on failed request', async () => {
    const errorData = { detail: 'Not found' };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => errorData,
    });

    await expect(apiFetch('/test')).rejects.toThrow(ApiError);
    await expect(apiFetch('/test')).rejects.toThrow('API Error: 404 Not Found');
  });

  it('should handle error when response.json() fails', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => {
        throw new Error('Invalid JSON');
      },
    });

    await expect(apiFetch('/test')).rejects.toThrow(ApiError);
  });
});

describe('HTTP Method Helpers', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('apiGet should make GET request', async () => {
    const mockData = { id: 1 };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    await apiGet('/test');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({
        method: 'GET',
      })
    );
  });

  it('apiPost should make POST request with data', async () => {
    const postData = { name: 'Test' };
    const mockResponse = { id: 1, ...postData };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockResponse,
    });

    await apiPost('/test', postData);

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(postData),
      })
    );
  });

  it('apiPost should handle request without data', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    await apiPost('/test');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({
        method: 'POST',
        body: undefined,
      })
    );
  });

  it('apiPut should make PUT request', async () => {
    const putData = { name: 'Updated' };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => putData,
    });

    await apiPut('/test/1', putData);

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test/1',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(putData),
      })
    );
  });

  it('apiPatch should make PATCH request', async () => {
    const patchData = { name: 'Patched' };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => patchData,
    });

    await apiPatch('/test/1', patchData);

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test/1',
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify(patchData),
      })
    );
  });

  it('apiDelete should make DELETE request', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    await apiDelete('/test/1');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test/1',
      expect.objectContaining({
        method: 'DELETE',
      })
    );
  });
});
