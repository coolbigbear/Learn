import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../api/client.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const performLogout = useCallback(() => {
    api.setToken(null);
    setUser(null);
  }, []);

  const handleUnauthorized = useCallback(() => {
    performLogout();
    navigate('/login', { replace: true });
  }, [performLogout, navigate]);

  useEffect(() => {
    // Register the global 401 handler so client.js can call it
    api.setOnUnauthorized(handleUnauthorized);

    // On mount, check if the stored token is already expired
    const token = api.getToken();
    if (token) {
      if (api.isTokenExpired()) {
        // Token is expired — clear it and redirect to login
        api.clearToken();
        setUser(null);
      } else {
        // Token exists and is not expired — user is considered logged in.
        // Decode the payload to extract user info (if available).
        const payload = api.decodeToken(token);
        setUser({
          token,
          userId: payload?.sub ? parseInt(payload.sub, 10) : undefined,
          username: payload?.username,
        });
      }
    }
    setLoading(false);

    return () => {
      // Cleanup: unregister the handler when provider unmounts
      api.setOnUnauthorized(null);
    };
  }, [handleUnauthorized]);

  const login = useCallback(async (username, password) => {
    const data = await api.login(username, password);
    api.setToken(data.token);
    setUser({ id: data.id, username: data.username, token: data.token });
    return data;
  }, []);

  const register = useCallback(async (username, password) => {
    const data = await api.register(username, password);
    api.setToken(data.token);
    setUser({ id: data.id, username: data.username, token: data.token });
    return data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      // Even if the API call fails, clear local state
    }
    performLogout();
    navigate('/', { replace: true });
  }, [performLogout, navigate]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default useAuth;