const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('auth_token');
}

function setToken(token) {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

async function request(path, options = {}) {
  const { method = 'GET', body, auth = false } = options;

  const headers = {
    'Content-Type': 'application/json',
  };

  if (auth) {
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

export { getToken, setToken };