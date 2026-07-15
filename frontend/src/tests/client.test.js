import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

/**
 * Helper: create fresh localStorage and fetch mocks for each test.
 * Uses vi.mock with importOriginal to ensure client.js is always fresh
 * and localStorage/fetch are mocked at module-load time.
 */

let mockFetch;

// We mock the entire client module using importOriginal to keep all exports,
// then add localStorage stubs at the top of the file.
vi.mock('../api/client.js', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    // localStorage is stubbed globally below — these are the real setToken/getToken etc.
  };
});

// Mock localStorage and fetch globally before each test
beforeEach(() => {
  const store = {};
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key) => store[key] ?? null),
    setItem: vi.fn((key, value) => { store[key] = value; }),
    removeItem: vi.fn((key) => { delete store[key]; }),
    clear: vi.fn(() => { Object.keys(store).forEach(k => delete store[k]); }),
  });
  mockFetch = vi.fn();
  vi.stubGlobal('fetch', mockFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

// Helper to create a valid JWT
function createToken(payload) {
  const b64 = btoa(JSON.stringify(payload)).replace(/=/g, '');
  return `header.${b64}.signature`;
}

// Helper to set a token in localStorage
function setToken(token) {
  localStorage.setItem('auth_token', token);
}

describe('decodeToken', () => {
  it('decodes a valid JWT token payload', async () => {
    const { decodeToken } = await import('../api/client.js');
    const token = createToken({ sub: '1', exp: 9999999999, iat: 1000000000 });
    const result = decodeToken(token);
    expect(result.sub).toBe('1');
    expect(result.exp).toBe(9999999999);
  });

  it('returns null for malformed token', async () => {
    const { decodeToken } = await import('../api/client.js');
    expect(decodeToken('not-a-jwt')).toBeNull();
    expect(decodeToken('only.two')).toBeNull();
    expect(decodeToken('')).toBeNull();
    expect(decodeToken(null)).toBeNull();
  });

  it('returns null for token with invalid base64 payload', async () => {
    const { decodeToken } = await import('../api/client.js');
    expect(decodeToken('header.!!!invalid!!!.signature')).toBeNull();
  });
});

describe('isTokenExpired', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-01-15T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns true when no token exists', async () => {
    const { isTokenExpired } = await import('../api/client.js');
    expect(isTokenExpired()).toBe(true);
  });

  it('returns false when token has not expired', async () => {
    const { isTokenExpired } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 9999999999 }));
    expect(isTokenExpired()).toBe(false);
  });

  it('returns true when token is expired', async () => {
    const { isTokenExpired } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 1000000000 }));
    expect(isTokenExpired()).toBe(true);
  });

  it('returns true for token with no exp claim', async () => {
    const { isTokenExpired } = await import('../api/client.js');
    setToken(createToken({ sub: '1' }));
    expect(isTokenExpired()).toBe(true);
  });
});

describe('checkAuth', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-01-15T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns true when token is valid', async () => {
    const { checkAuth, getToken } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 9999999999 }));
    expect(checkAuth()).toBe(true);
    expect(getToken()).not.toBeNull();
  });

  it('returns false and clears token when expired', async () => {
    const { checkAuth, getToken } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 1000000000 }));
    expect(checkAuth()).toBe(false);
    expect(getToken()).toBeNull();
  });

  it('returns false when no token exists', async () => {
    const { checkAuth } = await import('../api/client.js');
    expect(checkAuth()).toBe(false);
  });
});

describe('setOnUnauthorized / clearToken', () => {
  it('fires the registered callback on clearToken', async () => {
    const { setOnUnauthorized, clearToken } = await import('../api/client.js');
    const callback = vi.fn();
    setOnUnauthorized(callback);
    clearToken();
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('clears localStorage token on clearToken', async () => {
    const { clearToken, getToken } = await import('../api/client.js');
    setToken('some-token');
    expect(getToken()).toBe('some-token');
    clearToken();
    expect(getToken()).toBeNull();
  });

  it('does nothing when no callback registered', async () => {
    const { clearToken } = await import('../api/client.js');
    expect(() => clearToken()).not.toThrow();
  });
});

describe('request() 401 handling', () => {
  it('fires unauthorized callback on 401 response from server', async () => {
    const { setOnUnauthorized, getToken, getLesson } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 9999999999 }));

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: 'Invalid or expired token' }),
    });

    const cb = vi.fn();
    setOnUnauthorized(cb);

    await expect(getLesson('test-slug')).rejects.toThrow('Invalid or expired token');
    expect(cb).toHaveBeenCalledTimes(1);
    expect(getToken()).toBeNull();
  });

  it('pre-flight check catches expired token before API call', async () => {
    const { getLesson } = await import('../api/client.js');
    setToken(createToken({ sub: '1', exp: 1000000000 }));

    await expect(getLesson('test-slug')).rejects.toThrow('Invalid or expired token');
    // No API call should have been made — caught pre-flight
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('non-auth request does not check token', async () => {
    const { getVersion } = await import('../api/client.js');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ version: '1.0.0' }),
    });

    const result = await getVersion();
    expect(result.version).toBe('1.0.0');
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
});