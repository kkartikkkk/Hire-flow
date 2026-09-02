import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Job, PaginatedResponse } from '../types';
import { jobService } from '../services/jobService';

export default function JobListPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<PaginatedResponse<Job> | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await jobService.list({
        page,
        page_size: 10,
        status: statusFilter || undefined,
        location: locationFilter || undefined,
        search: search || undefined,
      });
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter, locationFilter]);

  useEffect(() => { fetchJobs(); }, [fetchJobs]);

  const handleSearch = () => { setPage(1); fetchJobs(); };

  return (
    <div className="page-shell">
      <div className="page-header">
        <h1>Job Postings</h1>
        <button className="btn btn-primary" onClick={() => navigate('/jobs/new')}>+ New Job</button>
      </div>

      <div className="filters-bar">
        <input type="text" placeholder="Search jobs…" value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSearch()} className="filter-input search-input" />
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }} className="filter-input">
          <option value="">All Status</option>
          <option value="OPEN">Open</option>
          <option value="CLOSED">Closed</option>
        </select>
        <input type="text" placeholder="Location" value={locationFilter} onChange={e => setLocationFilter(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSearch()} className="filter-input" />
        <button className="btn btn-secondary" onClick={handleSearch}>Apply</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading-state">Loading jobs…</div>
      ) : !data || data.items.length === 0 ? (
        <div className="empty-state">
          <p>No jobs found</p>
          <button className="btn btn-primary" onClick={() => navigate('/jobs/new')}>Create your first job</button>
        </div>
      ) : (
        <>
          <div className="job-grid">
            {data.items.map(job => (
              <div key={job.id} className="job-card" onClick={() => navigate(`/jobs/${job.id}`)}>
                <div className="job-card-header">
                  <h3 className="job-card-title">{job.title}</h3>
                  <span className={`badge badge-${job.status.toLowerCase()}`}>{job.status}</span>
                </div>
                <div className="job-card-meta">
                  <span>{job.location}</span>
                  <span className="meta-sep">·</span>
                  <span>{job.employment_type}</span>
                  {job.salary_range && <><span className="meta-sep">·</span><span>{job.salary_range}</span></>}
                </div>
                <p className="job-card-skills">{job.required_skills}</p>
                <div className="job-card-footer">
                  <span className="text-secondary">{new Date(job.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button className="btn btn-secondary btn-sm" disabled={!data.has_previous} onClick={() => setPage(p => p - 1)}>Previous</button>
            <span className="pagination-info">Page {data.page} of {data.total_pages} · {data.total} jobs</span>
            <button className="btn btn-secondary btn-sm" disabled={!data.has_next} onClick={() => setPage(p => p + 1)}>Next</button>
          </div>
        </>
      )}
    </div>
  );
}
