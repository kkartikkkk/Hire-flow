import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { Job } from '../types';
import { jobService } from '../services/jobService';

export default function JobDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    jobService.get(id).then(setJob).catch(() => setError('Job not found')).finally(() => setLoading(false));
  }, [id]);

  const handleClose = async () => {
    if (!id || !confirm('Close this job posting?')) return;
    setActionLoading(true);
    try {
      const updated = await jobService.close(id);
      setJob(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to close job');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id || !confirm('Delete this job permanently?')) return;
    setActionLoading(true);
    try {
      await jobService.delete(id);
      navigate('/jobs');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete job');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="page-shell"><div className="loading-state">Loading…</div></div>;
  if (error && !job) return <div className="page-shell"><div className="alert alert-error">{error}</div><button className="btn btn-secondary" onClick={() => navigate('/jobs')}>Back to Jobs</button></div>;
  if (!job) return null;

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <h1>{job.title}</h1>
          <span className={`badge badge-${job.status.toLowerCase()}`}>{job.status}</span>
        </div>
        <div className="header-actions">
          {job.status === 'OPEN' && (
            <>
              <button className="btn btn-secondary" onClick={() => navigate(`/jobs/${id}/edit`)}>Edit</button>
              <button className="btn btn-warning" onClick={handleClose} disabled={actionLoading}>Close</button>
            </>
          )}
          <button className="btn btn-danger" onClick={handleDelete} disabled={actionLoading}>Delete</button>
        </div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="detail-card">
        <div className="detail-grid">
          <div className="detail-item">
            <span className="detail-label">Location</span>
            <span className="detail-value">{job.location}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Employment Type</span>
            <span className="detail-value">{job.employment_type}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Experience Required</span>
            <span className="detail-value">{job.experience_required} years</span>
          </div>
          {job.salary_range && (
            <div className="detail-item">
              <span className="detail-label">Salary Range</span>
              <span className="detail-value">{job.salary_range}</span>
            </div>
          )}
          <div className="detail-item">
            <span className="detail-label">Created</span>
            <span className="detail-value">{new Date(job.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        <div className="detail-section">
          <h2>Required Skills</h2>
          <div className="skills-list">
            {job.required_skills.split(',').map((skill, i) => (
              <span key={i} className="skill-tag">{skill.trim()}</span>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <h2>Description</h2>
          <p className="detail-text">{job.description}</p>
        </div>
      </div>
    </div>
  );
}
