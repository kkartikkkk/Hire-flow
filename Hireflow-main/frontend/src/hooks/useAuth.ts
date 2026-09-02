/**
 * Authentication hook — manages auth state via localStorage.
 */

import { useState, useCallback, useEffect } from 'react';
import type { Recruiter, TokenResponse } from '../types';
import { api } from '../services/api';

interface AuthState {
  user: Recruiter | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    isLoading: true,
  });

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setState({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }
    try {
      const user = await api.get<Recruiter>('/auth/me');
      setState({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('access_token');
      setState({ user: null, isAuthenticated: false, isLoading: false });
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<TokenResponse>('/auth/login', { email, password });
    localStorage.setItem('access_token', res.access_token);
    await fetchUser();
  }, [fetchUser]);

  const register = useCallback(async (name: string, email: string, password: string) => {
    await api.post<Recruiter>('/auth/register', { name, email, password });
    // Auto-login after registration
    await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setState({ user: null, isAuthenticated: false, isLoading: false });
  }, []);

  return { ...state, login, register, logout };
}
