import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('nyaysetu_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('nyaysetu_access_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const storedToken = localStorage.getItem('nyaysetu_access_token');
      if (storedToken) {
        try {
          const profile = await authApi.getProfile();
          setUser(profile);
          localStorage.setItem('nyaysetu_user', JSON.stringify(profile));
        } catch {
          // Token expired or invalid
          setUser(null);
          setToken(null);
          localStorage.removeItem('nyaysetu_access_token');
          localStorage.removeItem('nyaysetu_refresh_token');
          localStorage.removeItem('nyaysetu_user');
        }
      }
      setLoading(false);
    }
    loadUser();
  }, []);

  const login = async (username, password) => {
    const data = await authApi.login(username, password);
    localStorage.setItem('nyaysetu_access_token', data.access);
    localStorage.setItem('nyaysetu_refresh_token', data.refresh);
    setToken(data.access);

    // Fetch user profile
    const profile = await authApi.getProfile();
    setUser(profile);
    localStorage.setItem('nyaysetu_user', JSON.stringify(profile));
    return profile;
  };

  const register = async (userData) => {
    return authApi.register(userData);
  };

  const verifyOtp = async (email, otp) => {
    return authApi.verifyOtp(email, otp);
  };

  const resendOtp = async (email) => {
    return authApi.resendOtp(email);
  };

  const logout = () => {
    localStorage.removeItem('nyaysetu_access_token');
    localStorage.removeItem('nyaysetu_refresh_token');
    localStorage.removeItem('nyaysetu_user');
    setUser(null);
    setToken(null);
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    isAdmin: user?.role === 'ADMIN',
    login,
    register,
    verifyOtp,
    resendOtp,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
