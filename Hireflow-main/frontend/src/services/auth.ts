import { api } from './api';
import type { Recruiter, TokenResponse } from '../types';

export const authService = {
  login(email: string, password: string): Promise<TokenResponse> {
    return api.post<TokenResponse>('/auth/login', { email, password });
  },

  register(name: string, email: string, password: string): Promise<Recruiter> {
    return api.post<Recruiter>('/auth/register', { name, email, password });
  },

  getCurrentUser(): Promise<Recruiter> {
    return api.get<Recruiter>('/auth/me');
  },
};
