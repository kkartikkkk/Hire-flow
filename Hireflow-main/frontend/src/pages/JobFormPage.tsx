import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { JobCreate, JobUpdate, Job } from '../types';
import { jobService } from '../services/jobService';

interface Props {
  mode: 'create' | 'edit';
}

export default function JobFormPage({ mode }: Props) {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(mode === 'edit');
  const [error, setError] = useState('');

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [experienceRequired, setExperienceRequired] = useState(0);
  const [location, setLocation] = useState('');
  const [employmentType, setEmploymentType] = useState('Full-time');
  const [salaryRange, setSalaryRange] = useState('');

  useEffect(() => {
    if (mode === 'edit' && id) {
      jobService.get(id).then((job: Job) => {
        setTitle(job.title);
        setDescription(job.description);
        setRequiredSkills(job.required_skills);
        setExperienceRequired(job.experience_required);
        setLocation(job.location);
        setEmploymentType(job.employment_type);
        setSalaryRange(job.salary_range || '');
        setFetching(false);
      }).catch(() => {
        setError('Failed to load job');
        setFetching(false);
      });
    }
  }, [mode, id]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'create') {
        const data: JobCreate = { title, description, required_skills: requiredSkills, experience_required: experienceRequired, location, employment_type: employmentType, salary_range: salaryRange || undefined };
        const job = await jobService.create(data);
        navigate(`/jobs/${job.id}`);
      } else if (id) {
        const data: JobUpdate = { title, description, required_skills: requiredSkills, experience_required: experienceRequired, location, employment_type: employmentType, salary_range: salaryRange || undefined };
        await jobService.update(id, data);
        navigate(`/jobs/${id}`);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save job');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) return <div className="page-shell"><div className="loading-state">Loading…</div></div>;

  return (
    <div className="page-shell">
      <div className="page-header">
        <h1>{mode === 'create' ? 'Create Job' : 'Edit Job'}</h1>
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-group">
          <label htmlFor="job-title">Title *</label>
          <input id="job-title" type="text" value={title} onChange={e => setTitle(e.target.value)} placeholder="Senior Python Developer" required minLength={3} maxLength={255} />
        </div>
        <div className="form-group">
          <label htmlFor="job-desc">Description *</label>
          <textarea id="job-desc" value={description} onChange={e => setDescription(e.target.value)} placeholder="Full job description…" required minLength={10} rows={5} />
        </div>
        <div className="form-group">
          <label htmlFor="job-skills">Required Skills *</label>
          <input id="job-skills" type="text" value={requiredSkills} onChange={e => setRequiredSkills(e.target.value)} placeholder="Python, FastAPI, PostgreSQL" required minLength={2} />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="job-exp">Experience (years)</label>
            <input id="job-exp" type="number" value={experienceRequired} onChange={e => setExperienceRequired(Number(e.target.value))} min={0} max={50} />
          </div>
          <div className="form-group">
            <label htmlFor="job-type">Employment Type *</label>
            <select id="job-type" value={employmentType} onChange={e => setEmploymentType(e.target.value)}>
              <option>Full-time</option>
              <option>Part-time</option>
              <option>Contract</option>
              <option>Internship</option>
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="job-location">Location *</label>
            <input id="job-location" type="text" value={location} onChange={e => setLocation(e.target.value)} placeholder="Remote" required minLength={2} />
          </div>
          <div className="form-group">
            <label htmlFor="job-salary">Salary Range</label>
            <input id="job-salary" type="text" value={salaryRange} onChange={e => setSalaryRange(e.target.value)} placeholder="$120k - $160k" />
          </div>
        </div>
        <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
          {loading ? 'Saving…' : mode === 'create' ? 'Create Job' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
