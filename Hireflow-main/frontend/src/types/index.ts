/**
 * Shared TypeScript type definitions.
 */

/** Generic paginated API response. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

/** Generic API error response. */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

/** Health check response. */
export interface HealthResponse {
  status: string;
  timestamp: string;
}

/** Recruiter (current user). */
export interface Recruiter {
  id: string;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
}

/** Auth token response. */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/** Job posting. */
export interface Job {
  id: string;
  recruiter_id: string;
  title: string;
  description: string;
  required_skills: string;
  experience_required: number;
  location: string;
  employment_type: string;
  salary_range: string | null;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  updated_at: string;
}

/** Job creation payload. */
export interface JobCreate {
  title: string;
  description: string;
  required_skills: string;
  experience_required: number;
  location: string;
  employment_type: string;
  salary_range?: string;
}

/** Job update payload (all optional). */
export interface JobUpdate {
  title?: string;
  description?: string;
  required_skills?: string;
  experience_required?: number;
  location?: string;
  employment_type?: string;
  salary_range?: string;
}

/** Candidate details. */
export interface Candidate {
  id: string;
  job_id: string;
  name: string;
  email: string;
  phone: string;
  resume_filename: string | null;
  skills: string;
  experience: string;
  education: string;
  fit_score: number | null;
  fit_reason: string | null;
  status: 'ACTIVE' | 'SHORTLISTED' | 'REJECTED' | 'HIRED';
  notes: string | null;
  parsed_resume: string | null;
  parsed_at: string | null;
  created_at: string;
  updated_at: string;
}
