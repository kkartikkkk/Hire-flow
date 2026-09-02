import { api } from './api';
import type { Candidate, PaginatedResponse } from '../types';

export interface CandidateListParams {
  page?: number;
  page_size?: number;
  status?: string;
  job_id?: string;
  experience?: string;
  created_date?: string; // YYYY-MM-DD
  search?: string;
}

export const candidatesService = {
  create(payload: Omit<Candidate, 'id' | 'created_at' | 'updated_at'>): Promise<Candidate> {
    return api.post<Candidate>('/candidates', payload);
  },

  list(params: CandidateListParams = {}): Promise<PaginatedResponse<Candidate>> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', String(params.page));
    if (params.page_size) searchParams.set('page_size', String(params.page_size));
    if (params.status) searchParams.set('status', params.status);
    if (params.job_id) searchParams.set('job_id', params.job_id);
    if (params.experience) searchParams.set('experience', params.experience);
    if (params.created_date) searchParams.set('created_date', params.created_date);
    if (params.search) searchParams.set('search', params.search);

    const qs = searchParams.toString();
    return api.get<PaginatedResponse<Candidate>>(`/candidates${qs ? `?${qs}` : ''}`);
  },

  get(id: string): Promise<Candidate> {
    return api.get<Candidate>(`/candidates/${id}`);
  },

  update(id: string, payload: Partial<Omit<Candidate, 'id' | 'created_at' | 'updated_at'>>): Promise<Candidate> {
    return api.put<Candidate>(`/candidates/${id}`, payload);
  },

  delete(id: string): Promise<void> {
    return api.delete<void>(`/candidates/${id}`);
  },
};

// Export candidateService alias for compatibility
export const candidateService = candidatesService;
