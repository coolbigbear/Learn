import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import * as api from '../api/client.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      // Token exists — user is considered logged in.
      // The token's validity can be checked on first API call.
      setUser({ token });
    }
    setLoading(false);
  }, []);

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
    api.setToken(null);
    setUser(null);
  }, []);

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