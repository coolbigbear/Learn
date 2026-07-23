const API_BASE = '/api';

/** Callback invoked when any API call receives a 401 Unauthorized response. */
let _onUnauthorized = null;

/**
 * Register a callback that fires on 401 responses.
 * The auth provider uses this to clear state and redirect to login.
 */
export function setOnUnauthorized(cb) {
  _onUnauthorized = cb;
}

function getToken() {
  try {
    return localStorage.getItem('auth_token');
  } catch {
    return null;
  }
}

function setToken(token) {
  try {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  } catch {
    // localStorage may be unavailable (private browsing, quota, etc.)
    // Fail gracefully — treat as not authenticated.
  }
}

/**
 * Decode a JWT token's payload without verifying the signature.
 * Returns null if the token is malformed.
 */
function decodeToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = parts[1];
    // Base64url decode → JSON
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

/**
 * Check if a JWT token is expired by inspecting its `exp` claim.
 * Returns true if the token is missing, malformed, or past its expiration.
 */
export function isTokenExpired() {
  const token = getToken();
  if (!token) return true;
  const payload = decodeToken(token);
  if (!payload || !payload.exp) return true;
  // exp is in seconds; Date.now() is in milliseconds
  return Date.now() >= payload.exp * 1000;
}

/**
 * Clear the stored token and signal unauthorized state.
 * Used internally on 401 responses and by the auth provider.
 */
export function clearToken() {
  setToken(null);
  if (_onUnauthorized) {
    _onUnauthorized();
  }
}

/**
 * Verify the token is still valid before making an auth-required call.
 * Returns true if the token exists and is not expired.
 */
export function checkAuth() {
  if (isTokenExpired()) {
    if (getToken()) {
      // Token exists but is expired — clear it
      clearToken();
    }
    return false;
  }
  return true;
}

async function request(path, options = {}) {
  const { method = 'GET', body, auth = false } = options;

  const headers = {
    'Content-Type': 'application/json',
  };

  if (auth) {
    // Pre-flight check: if the token is already expired, fail fast
    // instead of waiting for a server round-trip.
    if (!checkAuth()) {
      const err = new Error('Invalid or expired token');
      err.status = 401;
      throw err;
    }

    const token = getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body !== undefined) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${path}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const err = new Error(error.detail || `Request failed with status ${response.status}`);
    err.status = response.status;

    // Global 401 handler — clear token and redirect
    if (response.status === 401) {
      clearToken();
    }

    throw err;
  }

  return response.json();
}

// Auth API
export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { username, password },
  });
}

export function register(username, password) {
  return request('/auth/register', {
    method: 'POST',
    body: { username, password },
  });
}

export function logout() {
  return request('/auth/logout', {
    method: 'POST',
    auth: true,
  });
}

// Lessons API
export function getLessons() {
  return request('/lessons', { auth: true });
}

export function getLessonsByPath() {
  return request('/lessons/by-path', { auth: true });
}

export function getLesson(slug) {
  return request(`/lessons/${slug}`, { auth: true });
}

// Exercises API
export function runExercise(exerciseId, code) {
  return request(`/exercises/${exerciseId}/run`, {
    method: 'POST',
    body: { code },
    auth: true,
  });
}

export function submitExercise(exerciseId, code) {
  return request(`/exercises/${exerciseId}/submit`, {
    method: 'POST',
    body: { code },
    auth: true,
  });
}

// Progress API
export function getProgress() {
  return request('/progress', { auth: true });
}

export function getLessonProgress(lessonSlug) {
  return request(`/progress/${lessonSlug}`, { auth: true });
}

// Health
export function health() {
  return request('/health');
}

// Version
export function getVersion() {
  return request('/version');
}

export { getToken, setToken, decodeToken };