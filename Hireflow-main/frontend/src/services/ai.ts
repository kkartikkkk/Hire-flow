import type { Candidate } from '../types';

export const aiService = {
  uploadResume(
    candidateId: string,
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<Candidate> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('candidate_id', candidateId);
      formData.append('file', file);

      xhr.open('POST', '/api/v1/candidates/upload', true);

      // Add authorization headers if token exists
      const token = localStorage.getItem('access_token');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      // Track progress
      if (xhr.upload && onProgress) {
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            onProgress(percent);
          }
        };
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText) as Candidate;
            resolve(response);
          } catch (err) {
            reject(new Error('Failed to parse upload response.'));
          }
        } else {
          try {
            const errorBody = JSON.parse(xhr.responseText);
            reject(new Error(errorBody?.error?.message || 'Upload failed.'));
          } catch {
            reject(new Error(`Upload failed with status code ${xhr.status}.`));
          }
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network error during file upload.'));
      };

      xhr.send(formData);
    });
  },

  uploadDirect(
    jobId: string,
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<Candidate> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('job_id', jobId);
      formData.append('file', file);

      xhr.open('POST', '/api/v1/candidates/upload-direct', true);

      const token = localStorage.getItem('access_token');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      if (xhr.upload && onProgress) {
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            onProgress(percent);
          }
        };
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText) as Candidate;
            resolve(response);
          } catch (err) {
            reject(new Error('Failed to parse upload response.'));
          }
        } else {
          try {
            const errorBody = JSON.parse(xhr.responseText);
            reject(new Error(errorBody?.error?.message || 'Upload failed.'));
          } catch {
            reject(new Error(`Upload failed with status code ${xhr.status}.`));
          }
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network error during file upload.'));
      };

      xhr.send(formData);
    });
  },

  parse(id: string): Promise<Candidate> {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(`/api/v1/candidates/${id}/parse`, {
      method: 'POST',
      headers,
    }).then(async (response) => {
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody?.error?.message || 'AI resume parsing failed.');
      }
      return response.json() as Promise<Candidate>;
    });
  },

  calculateFitScore(id: string): Promise<Candidate> {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(`/api/v1/candidates/${id}/fit-score`, {
      method: 'POST',
      headers,
    }).then(async (response) => {
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody?.error?.message || 'AI fit scoring failed.');
      }
      return response.json() as Promise<Candidate>;
    });
  },

  getParsed(id: string): Promise<Candidate> {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(`/api/v1/candidates/${id}/parsed`, {
      method: 'GET',
      headers,
    }).then(async (response) => {
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody?.error?.message || 'Failed to retrieve parsed details.');
      }
      return response.json() as Promise<Candidate>;
    });
  },
};
