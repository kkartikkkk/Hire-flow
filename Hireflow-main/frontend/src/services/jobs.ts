import { api } from './api';
import type { Job, JobCreate, JobUpdate, PaginatedResponse } from '../types';

export interface JobListParams {
  page?: number;
  page_size?: number;
  status?: string;
  location?: string;
  employment_type?: string;
  search?: string;
}

export const jobsService = {
  list(params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', String(params.page));
    if (params.page_size) searchParams.set('page_size', String(params.page_size));
    if (params.status) searchParams.set('status', params.status);
    if (params.location) searchParams.set('location', params.location);
    if (params.employment_type) searchParams.set('employment_type', params.employment_type);
    if (params.search) searchParams.set('search', params.search);
    const qs = searchParams.toString();
    return api.get<PaginatedResponse<Job>>(`/jobs${qs ? `?${qs}` : ''}`);
  },

  get(id: string): Promise<Job> {
    return api.get<Job>(`/jobs/${id}`);
  },

  create(data: JobCreate): Promise<Job> {
    return api.post<Job>('/jobs', data);
  },

  update(id: string, data: JobUpdate): Promise<Job> {
    return api.put<Job>(`/jobs/${id}`, data);
  },

  close(id: string): Promise<Job> {
    return api.patch<Job>(`/jobs/${id}/close`);
  },

  delete(id: string): Promise<void> {
    return api.delete<void>(`/jobs/${id}`);
  },

  getDashboardStats(): Promise<any> {
    return api.get<any>('/dashboard/stats');
  },
};

// Export both names to satisfy backward compatibility
export const jobService = jobsService;
