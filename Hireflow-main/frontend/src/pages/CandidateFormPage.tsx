import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { Candidate, Job } from '../types';
import { candidateService } from '../services/candidateService';
import { jobService } from '../services/jobService';
import { aiService } from '../services/ai';

type FileStatus = 'pending' | 'uploading' | 'parsing' | 'success' | 'error';
interface FileUploadState {
  file: File;
  status: FileStatus;
  progress: number;
  error?: string;
}

interface Props {
  mode: 'create' | 'edit';
}

export default function CandidateFormPage({ mode }: Props) {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(mode === 'edit');
  const [error, setError] = useState('');

  // Dropdown options
  const [jobs, setJobs] = useState<Job[]>([]);

  // Direct Bulk Resume Upload State
  const [uploadFiles, setUploadFiles] = useState<FileUploadState[]>([]);
  const [isBulkUploading, setIsBulkUploading] = useState(false);

  // Form fields
  const [jobId, setJobId] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [resumeFilename, setResumeFilename] = useState('');
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [education, setEducation] = useState('');
  const [status, setStatus] = useState<'ACTIVE' | 'SHORTLISTED' | 'REJECTED' | 'HIRED'>('ACTIVE');
  const [notes, setNotes] = useState('');

  const handleDirectUpload = async () => {
    if (!jobId) {
      setError('Please select an associated job posting first.');
      return;
    }
    if (uploadFiles.length === 0) {
      setError('Please select at least one resume file.');
      return;
    }

    setError('');
    setIsBulkUploading(true);

    let hasError = false;

    for (let i = 0; i < uploadFiles.length; i++) {
      const fileState = uploadFiles[i];
      if (fileState.status === 'success') continue;

      setUploadFiles(prev => prev.map((f, idx) => 
        idx === i ? { ...f, status: 'uploading', progress: 0, error: undefined } : f
      ));

      try {
        await aiService.uploadDirect(jobId, fileState.file, (progress) => {
          setUploadFiles(prev => prev.map((f, idx) => {
            if (idx === i) {
               return { ...f, progress, status: progress >= 100 ? 'parsing' : 'uploading' };
            }
            return f;
          }));
        });
        
        setUploadFiles(prev => prev.map((f, idx) => 
          idx === i ? { ...f, status: 'success', progress: 100 } : f
        ));
      } catch (err: unknown) {
        hasError = true;
        setUploadFiles(prev => prev.map((f, idx) => 
          idx === i ? { ...f, status: 'error', error: err instanceof Error ? err.message : 'Failed' } : f
        ));
      }
    }

    setIsBulkUploading(false);
    
    if (!hasError) {
      navigate('/candidates');
    } else {
      setError('Some files failed to upload. Please check the list below.');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        file,
        status: 'pending' as FileStatus,
        progress: 0
      }));
      setUploadFiles(prev => [...prev, ...newFiles]);
      // Reset the input value so the same file or additional files can be selected sequentially without issues
      e.target.value = '';
    }
  };
  
  const removeUploadFile = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
  };

  useEffect(() => {
    // Load recruiter's open jobs for candidate job association
    jobService.list({ page: 1, page_size: 100 })
      .then(res => setJobs(res.items.filter(j => j.status === 'OPEN')))
      .catch(() => setError('Failed to load jobs list'));

    if (mode === 'edit' && id) {
      candidateService.get(id).then((candidate: Candidate) => {
        setJobId(candidate.job_id);
        setName(candidate.name);
        setEmail(candidate.email);
        setPhone(candidate.phone);
        setResumeFilename(candidate.resume_filename || '');
        setSkills(candidate.skills);
        setExperience(candidate.experience);
        setEducation(candidate.education);
        setStatus(candidate.status);
        setNotes(candidate.notes || '');
        setFetching(false);
      }).catch(() => {
        setError('Failed to load candidate details');
        setFetching(false);
      });
    }
  }, [mode, id]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!jobId) {
      setError('Please select a job opening.');
      setLoading(false);
      return;
    }

    try {
      const payload = {
        job_id: jobId,
        name,
        email,
        phone,
        resume_filename: resumeFilename || null,
        skills,
        experience,
        education,
        status,
        notes: notes || null,
        fit_score: null,
        fit_reason: null,
        parsed_resume: null,
        parsed_at: null,
      };

      if (mode === 'create') {
        await candidateService.create(payload);
        navigate('/candidates');
      } else if (id) {
        await candidateService.update(id, payload);
        navigate('/candidates');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save candidate profile');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) return <div className="page-shell"><div className="loading-state">Loading…</div></div>;

  return (
    <div className="page-shell">
      <div className="page-header">
        <h1>{mode === 'create' ? 'Add Candidate' : 'Edit Candidate'}</h1>
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      
      {mode === 'create' && (
        <div className="detail-card" style={{ marginBottom: '2rem', border: '2px dashed var(--color-accent-light)', padding: '1.5rem', background: '#f8fafc' }}>
          <h2 style={{ fontSize: '1.15rem', color: 'var(--color-accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            ⚡ Bulk Resume Upload & AI Auto-Fill
          </h2>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
            Skip the manual form! Select a job, drop multiple resumes, and our AI will automatically parse details, create candidates, and generate fit scores.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', alignItems: 'end', marginBottom: '1rem' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="direct-job">1. Select Job Opening *</label>
              <select 
                id="direct-job" 
                value={jobId} 
                onChange={e => setJobId(e.target.value)} 
                disabled={isBulkUploading}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}
              >
                <option value="">-- Select Job Posting --</option>
                {jobs.map(job => (
                  <option key={job.id} value={job.id}>{job.title} ({job.location})</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="direct-file">2. Choose Resumes (PDF / DOCX) *</label>
              <input 
                id="direct-file" 
                type="file" 
                multiple={true}
                accept="application/pdf,.pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,.docx" 
                onChange={handleFileChange}
                disabled={isBulkUploading}
                style={{ width: '100%', padding: '0.4rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}
              />
            </div>

            <div>
              <button 
                type="button" 
                className="btn btn-primary btn-full" 
                disabled={!jobId || uploadFiles.length === 0 || isBulkUploading} 
                onClick={handleDirectUpload}
                style={{ height: '2.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'center' }}
              >
                {isBulkUploading ? 'Processing...' : `Upload & Parse ${uploadFiles.length} file(s)`}
              </button>
            </div>
          </div>

          {uploadFiles.length > 0 && (
            <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h4 style={{ fontSize: '0.875rem', margin: 0 }}>Selected Files:</h4>
              {uploadFiles.map((fileState, idx) => (
                <div key={idx} style={{ 
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
                  padding: '0.75rem', background: '#fff', border: '1px solid var(--color-border)', 
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem', overflow: 'hidden' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.875rem', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {fileState.file.name}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 
                        fileState.status === 'success' ? 'var(--color-success)' : 
                        fileState.status === 'error' ? 'var(--color-error)' : 
                        'var(--color-accent)' 
                      }}>
                        {fileState.status === 'pending' && 'Pending'}
                        {fileState.status === 'uploading' && `Uploading ${fileState.progress}%`}
                        {fileState.status === 'parsing' && 'AI Parsing...'}
                        {fileState.status === 'success' && '✅ Success'}
                        {fileState.status === 'error' && '❌ Failed'}
                      </span>
                    </div>
                    {(fileState.status === 'uploading' || fileState.status === 'parsing') && (
                      <div style={{ height: '4px', background: '#e2e8f0', borderRadius: '2px', overflow: 'hidden', marginTop: '0.25rem' }}>
                         <div style={{ height: '100%', width: `${fileState.progress}%`, background: 'var(--color-accent)', transition: 'width 0.2s' }}></div>
                      </div>
                    )}
                    {fileState.error && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-error)' }}>{fileState.error}</span>
                    )}
                  </div>
                  {fileState.status !== 'success' && !isBulkUploading && (
                    <button 
                      onClick={() => removeUploadFile(idx)} 
                      style={{ marginLeft: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-secondary)', fontSize: '1.25rem' }}
                      title="Remove file"
                    >×</button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {mode === 'create' && <h3 style={{ marginBottom: '1rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Or manually enter details below:</h3>}

      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-group">
          <label htmlFor="cand-job">Associated Job Opening *</label>
          <select 
            id="cand-job" 
            value={jobId} 
            onChange={e => setJobId(e.target.value)} 
            disabled={mode === 'edit'}
            required
          >
            <option value="">-- Select Job Posting --</option>
            {jobs.map(job => (
              <option key={job.id} value={job.id}>{job.title} ({job.location})</option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="cand-name">Candidate Name *</label>
            <input 
              id="cand-name" 
              type="text" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              placeholder="Alice Johnson" 
              required 
              maxLength={255} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="cand-status">Status *</label>
            <select 
              id="cand-status" 
              value={status} 
              onChange={e => setStatus(e.target.value as any)}
            >
              <option value="ACTIVE">Active</option>
              <option value="SHORTLISTED">Shortlisted</option>
              <option value="REJECTED">Rejected</option>
              <option value="HIRED">Hired</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="cand-email">Email Address *</label>
            <input 
              id="cand-email" 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              placeholder="alice.j@example.com" 
              required 
              maxLength={255} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="cand-phone">Phone Number *</label>
            <input 
              id="cand-phone" 
              type="text" 
              value={phone} 
              onChange={e => setPhone(e.target.value)} 
              placeholder="+1 555-0199" 
              required 
              maxLength={50} 
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="cand-resume-file">Resume Filename</label>
          <input 
            id="cand-resume-file" 
            type="text" 
            value={resumeFilename} 
            onChange={e => setResumeFilename(e.target.value)} 
            placeholder="alice_resume.pdf" 
            maxLength={255}
          />
        </div>

        <div className="form-group">
          <label htmlFor="cand-skills">Skills *</label>
          <textarea 
            id="cand-skills" 
            value={skills} 
            onChange={e => setSkills(e.target.value)} 
            placeholder="e.g. Python, Django, React, REST APIs" 
            required 
            rows={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="cand-exp">Work Experience *</label>
          <textarea 
            id="cand-exp" 
            value={experience} 
            onChange={e => setExperience(e.target.value)} 
            placeholder="e.g. 4 years Software Engineer at TechCorp" 
            required 
            rows={4}
          />
        </div>

        <div className="form-group">
          <label htmlFor="cand-edu">Education *</label>
          <textarea 
            id="cand-edu" 
            value={education} 
            onChange={e => setEducation(e.target.value)} 
            placeholder="e.g. B.S. in Computer Science, Georgia Tech" 
            required 
            rows={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="cand-notes">Notes / Comments</label>
          <textarea 
            id="cand-notes" 
            value={notes} 
            onChange={e => setNotes(e.target.value)} 
            placeholder="Interview feedback or candidate background comments…" 
            rows={3}
          />
        </div>

        <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
          {loading ? 'Saving…' : mode === 'create' ? 'Add Candidate' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
