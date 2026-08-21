import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('tracelens_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('tracelens_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const profile = await authService.getMe();
          setUser(profile);
          localStorage.setItem('tracelens_user', JSON.stringify(profile));
        } catch (err) {
          console.error('Session verification failed', err);
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (username, password) => {
    const data = await authService.login({ username, password });
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('tracelens_token', data.access_token);
    localStorage.setItem('tracelens_user', JSON.stringify(data.user));
    return data;
  };

  const register = async (userData) => {
    const data = await authService.register(userData);
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('tracelens_token', data.access_token);
    localStorage.setItem('tracelens_user', JSON.stringify(data.user));
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('tracelens_token');
    localStorage.removeItem('tracelens_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
