import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Candidate, Job } from '../types';
import { candidateService } from '../services/candidateService';
import { jobService } from '../services/jobService';
import { aiService } from '../services/ai';

export default function CandidateListPage() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Search & Filter State
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [jobFilter, setJobFilter] = useState('');
  const [experienceFilter, setExperienceFilter] = useState('');
  const [createdDateFilter, setCreatedDateFilter] = useState('');

  // Pagination State
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Selected candidate for details modal
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  // Upload & processing state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState('');
  const [actionState, setActionState] = useState<'idle' | 'uploading' | 'parsing' | 'scoring'>('idle');
  const [actionError, setActionError] = useState('');

  // Load jobs list for filtering and mapping
  useEffect(() => {
    jobService.list({ page: 1, page_size: 100 })
      .then(res => setJobs(res.items))
      .catch(() => console.error('Failed to load jobs list'));
  }, []);

  const fetchCandidates = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await candidateService.list({
        page,
        page_size: pageSize,
        search: search || undefined,
        status: statusFilter || undefined,
        job_id: jobFilter || undefined,
        experience: experienceFilter || undefined,
        created_date: createdDateFilter || undefined,
      });
      setCandidates(res.items);
      setTotalPages(res.total_pages);
      setTotalRecords(res.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve candidate list');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, statusFilter, jobFilter, experienceFilter, createdDateFilter]);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  // Handle Search and Filter submits
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCandidates();
  };

  const handleClearFilters = () => {
    setSearch('');
    setStatusFilter('');
    setJobFilter('');
    setExperienceFilter('');
    setCreatedDateFilter('');
    setPage(1);
  };

  const handleDelete = async (candidateId: string) => {
    if (!confirm('Are you sure you want to delete this candidate application permanently?')) return;
    try {
      await candidateService.delete(candidateId);
      if (selectedCandidate && selectedCandidate.id === candidateId) {
        setSelectedCandidate(null);
      }
      fetchCandidates();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to delete candidate');
    }
  };

  // Upload Resume handler
  const handleUploadResume = async (candidateId: string) => {
    if (!uploadFile) return;
    setActionState('uploading');
    setUploadError('');
    setUploadProgress(0);
    try {
      const updated = await aiService.uploadResume(candidateId, uploadFile, (percent: number) => {
        setUploadProgress(percent);
      });
      setSelectedCandidate(updated);
      setUploadFile(null);
      setUploadProgress(null);
      fetchCandidates();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : 'Failed to upload resume file.');
    } finally {
      setActionState('idle');
    }
  };

  // Parse Resume handler
  const handleTriggerParse = async (candidateId: string) => {
    setActionState('parsing');
    setActionError('');
    try {
      const updated = await aiService.parse(candidateId);
      setSelectedCandidate(updated);
      fetchCandidates();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'AI parsing service error.');
    } finally {
      setActionState('idle');
    }
  };

  // Calculate Fit Score handler
  const handleTriggerFitScore = async (candidateId: string) => {
    setActionState('scoring');
    setActionError('');
    try {
      const updated = await aiService.calculateFitScore(candidateId);
      setSelectedCandidate(updated);
      fetchCandidates();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'AI fit scoring service error.');
    } finally {
      setActionState('idle');
    }
  };

  const getJobTitle = (jobId: string) => {
    const job = jobs.find(j => j.id === jobId);
    return job ? job.title : 'Unknown Job';
  };

  // Safely parse fit score reason
  const parseFitReason = (fitReasonStr: string | null) => {
    if (!fitReasonStr) return null;
    try {
      return JSON.parse(fitReasonStr) as {
        strengths?: string[];
        missing_skills?: string[];
        recommendation?: string;
        summary?: string;
      };
    } catch {
      return {
        summary: fitReasonStr
      };
    }
  };

  return (
    <div className="page-shell">
      {/* Header */}
      <div className="page-header">
        <h1>Candidate Profiles</h1>
        <button className="btn btn-primary" onClick={() => navigate('/candidates/new')}>
          Add Candidate
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Filter and Search Bar */}
      <div className="detail-card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="search-input" style={{ fontSize: 'var(--font-size-xs)' }}>Search Name, Email, Skills</label>
              <input 
                id="search-input"
                type="text" 
                placeholder="Python, John, alice@..." 
                value={search} 
                onChange={e => setSearch(e.target.value)} 
                className="filter-input"
                style={{ width: '100%' }}
              />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="status-filter" style={{ fontSize: 'var(--font-size-xs)' }}>Application Status</label>
              <select 
                id="status-filter"
                value={statusFilter} 
                onChange={e => setStatusFilter(e.target.value)}
                className="filter-input"
                style={{ width: '100%' }}
              >
                <option value="">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="SHORTLISTED">Shortlisted</option>
                <option value="REJECTED">Rejected</option>
                <option value="HIRED">Hired</option>
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="job-filter" style={{ fontSize: 'var(--font-size-xs)' }}>Associated Job</label>
              <select 
                id="job-filter"
                value={jobFilter} 
                onChange={e => setJobFilter(e.target.value)}
                className="filter-input"
                style={{ width: '100%' }}
              >
                <option value="">All Jobs</option>
                {jobs.map(job => (
                  <option key={job.id} value={job.id}>{job.title}</option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="exp-filter" style={{ fontSize: 'var(--font-size-xs)' }}>Experience Details</label>
              <input 
                id="exp-filter"
                type="text" 
                placeholder="Senior, 3 years, etc." 
                value={experienceFilter} 
                onChange={e => setExperienceFilter(e.target.value)}
                className="filter-input"
                style={{ width: '100%' }}
              />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label htmlFor="date-filter" style={{ fontSize: 'var(--font-size-xs)' }}>Applied Date</label>
              <input 
                id="date-filter"
                type="date" 
                value={createdDateFilter} 
                onChange={e => setCreatedDateFilter(e.target.value)}
                className="filter-input"
                style={{ width: '100%' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={handleClearFilters}>
              Clear Filters
            </button>
            <button type="submit" className="btn btn-primary">
              Apply Filters
            </button>
          </div>
        </form>
      </div>

      {/* Candidate List Container */}
      {loading ? (
        <div className="loading-state">Loading candidate list…</div>
      ) : candidates.length === 0 ? (
        <div className="empty-state">
          <p>No candidates found matching the filters.</p>
        </div>
      ) : (
        <div className="job-grid">
          {candidates.map(candidate => {
            const fitScore = candidate.fit_score;
            let scoreColor = 'var(--color-text-secondary)';
            if (fitScore !== null) {
              if (fitScore >= 80) scoreColor = 'var(--color-success)';
              else if (fitScore >= 60) scoreColor = 'var(--color-warning)';
              else scoreColor = 'var(--color-error)';
            }

            return (
              <div 
                key={candidate.id} 
                className="job-card" 
                onClick={() => { setSelectedCandidate(candidate); setUploadError(''); setActionError(''); }}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}
              >
                <div>
                  <div className="job-card-header" style={{ margin: 0, display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <h3 className="job-card-title">{candidate.name}</h3>
                    <span className={`badge badge-${candidate.status.toLowerCase()}`}>{candidate.status}</span>
                  </div>
                  <div className="job-card-meta" style={{ marginTop: '0.25rem', marginBottom: 0 }}>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                      {getJobTitle(candidate.job_id)}
                    </span>
                    <span className="meta-sep">·</span>
                    <span>{candidate.email}</span>
                    <span className="meta-sep">·</span>
                    <span>{candidate.phone}</span>
                  </div>
                  {candidate.skills && (
                    <div style={{ marginTop: '0.5rem' }}>
                      <div className="skills-list">
                        {candidate.skills.split(/[\n,]+/).map(s => s.trim()).filter(Boolean).slice(0, 12).map((skill, idx) => (
                          <span key={idx} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Score & Actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }} onClick={e => e.stopPropagation()}>
                  {fitScore !== null && (
                    <div style={{ textAlign: 'center' }}>
                      <span style={{ display: 'block', fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                        Fit Score
                      </span>
                      <strong style={{ fontSize: 'var(--font-size-lg)', color: scoreColor }}>
                        {fitScore}%
                      </strong>
                    </div>
                  )}
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => navigate(`/candidates/${candidate.id}/edit`)}
                    >
                      Edit
                    </button>
                    <button 
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(candidate.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem', alignItems: 'center' }}>
          <button 
            className="btn btn-secondary btn-sm" 
            disabled={page === 1}
            onClick={() => setPage(prev => Math.max(1, prev - 1))}
          >
            Previous
          </button>
          <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Page {page} of {totalPages} ({totalRecords} records)
          </span>
          <button 
            className="btn btn-secondary btn-sm" 
            disabled={page === totalPages}
            onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
          >
            Next
          </button>
        </div>
      )}

      {/* Candidate Details Dialog Modal */}
      {selectedCandidate && (
        <div 
          className="modal-overlay" 
          style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1rem' }}
          onClick={() => setSelectedCandidate(null)}
        >
          <div 
            className="modal-container" 
            style={{ background: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-xl)', width: '100%', maxWidth: '850px', maxHeight: '90vh', overflowY: 'auto', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--color-border)', paddingBottom: '1rem' }}>
              <div>
                <h2 style={{ fontSize: 'var(--font-size-xl)' }}>{selectedCandidate.name}</h2>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                  Applying to: <strong style={{ color: 'var(--color-accent-light)' }}>{getJobTitle(selectedCandidate.job_id)}</strong>
                </p>
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={() => setSelectedCandidate(null)}
                style={{ borderRadius: 'var(--radius-full)', padding: '0.25rem 0.75rem' }}
              >
                Close
              </button>
            </div>

            {/* Error notifications */}
            {uploadError && <div className="alert alert-error">{uploadError}</div>}
            {actionError && <div className="alert alert-error">{actionError}</div>}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }} className="form-row">
              
              {/* Left Column: Candidate Info & Upload */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                
                {/* Profile fields */}
                <div className="detail-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="detail-item">
                    <span className="detail-label">Email Address</span>
                    <span className="detail-value">{selectedCandidate.email}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Phone Number</span>
                    <span className="detail-value">{selectedCandidate.phone}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status</span>
                    <span className="detail-value">
                      <span className={`badge badge-${selectedCandidate.status.toLowerCase()}`}>{selectedCandidate.status}</span>
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Resume Document</span>
                    <span className="detail-value" style={{ wordBreak: 'break-all' }}>
                      {selectedCandidate.resume_filename || 'No document uploaded'}
                    </span>
                  </div>
                </div>

                {/* Upload Action widget */}
                <div style={{ background: 'var(--color-surface)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px dashed var(--color-border)' }}>
                  <h4 style={{ fontSize: 'var(--font-size-sm)', marginBottom: '0.5rem' }}>Upload New Resume Document</h4>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <input 
                      type="file" 
                      accept=".pdf,.docx" 
                      onChange={e => setUploadFile(e.target.files?.[0] || null)}
                      style={{ fontSize: 'var(--font-size-xs)', flex: 1 }}
                    />
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => handleUploadResume(selectedCandidate.id)}
                      disabled={!uploadFile || actionState !== 'idle'}
                    >
                      {actionState === 'uploading' ? `Uploading ${uploadProgress || 0}%` : 'Upload'}
                    </button>
                  </div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                    Supports PDF and DOCX only (Max 5MB).
                  </p>
                </div>

                {/* Parser controls */}
                {selectedCandidate.parsed_resume && (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      className="btn btn-secondary" 
                      style={{ flex: 1 }}
                      onClick={() => handleTriggerParse(selectedCandidate.id)}
                      disabled={actionState !== 'idle'}
                    >
                      {actionState === 'parsing' ? 'Parsing AI...' : 'Re-run AI Parser'}
                    </button>
                    <button 
                      className="btn btn-primary" 
                      style={{ flex: 1 }}
                      onClick={() => handleTriggerFitScore(selectedCandidate.id)}
                      disabled={actionState !== 'idle'}
                    >
                      {actionState === 'scoring' ? 'Scoring AI...' : 'Generate Fit Score'}
                    </button>
                  </div>
                )}

                {/* Standard profile details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: 'var(--font-size-sm)', marginBottom: '0.25rem' }}>Skills</h3>
                    <div className="skills-list">
                      {selectedCandidate.skills ? (
                        selectedCandidate.skills.split(/[\n,]+/).map(s => s.trim()).filter(Boolean).map((skill, idx) => (
                          <span key={idx} className="skill-tag">{skill}</span>
                        ))
                      ) : (
                        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>No skills listed.</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <h3 style={{ fontSize: 'var(--font-size-sm)', marginBottom: '0.25rem' }}>Work Experience</h3>
                    <p style={{ whiteSpace: 'pre-wrap', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                      {selectedCandidate.experience}
                    </p>
                  </div>
                  <div>
                    <h3 style={{ fontSize: 'var(--font-size-sm)', marginBottom: '0.25rem' }}>Education</h3>
                    <p style={{ whiteSpace: 'pre-wrap', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                      {selectedCandidate.education}
                    </p>
                  </div>
                </div>

              </div>

              {/* Right Column: AI Fit Score Report */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', borderLeft: '1px solid var(--color-border)', paddingLeft: '2rem' }}>
                
                {selectedCandidate.fit_score !== null ? (
                  <>
                    {/* Score header */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ background: 'var(--color-surface)', borderRadius: 'var(--radius-lg)', padding: '1rem', textAlign: 'center', minWidth: '100px', border: '1px solid var(--color-border)' }}>
                        <span style={{ display: 'block', fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                          Fit Score
                        </span>
                        <strong style={{ fontSize: 'var(--font-size-2xl)', color: selectedCandidate.fit_score >= 80 ? 'var(--color-success)' : selectedCandidate.fit_score >= 60 ? 'var(--color-warning)' : 'var(--color-error)' }}>
                          {selectedCandidate.fit_score}%
                        </strong>
                      </div>
                      <div>
                        <h3 style={{ fontSize: 'var(--font-size-base)', margin: 0 }}>ATS Match Score</h3>
                        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                          Last assessed: {selectedCandidate.parsed_at ? new Date(selectedCandidate.parsed_at).toLocaleString() : 'N/A'}
                        </span>
                      </div>
                    </div>

                    {/* Fit details */}
                    {(() => {
                      const report = parseFitReason(selectedCandidate.fit_reason);
                      if (!report) return null;
                      return (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                          <div>
                            <h4 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-success)', marginBottom: '0.25rem' }}>Key Strengths</h4>
                            <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', margin: 0 }}>
                              {report.strengths?.map((str, idx) => <li key={idx} style={{ marginBottom: '0.25rem' }}>{str}</li>) || <li>No direct strengths listed.</li>}
                            </ul>
                          </div>

                          <div>
                            <h4 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-warning)', marginBottom: '0.25rem' }}>Missing Skills / Gaps</h4>
                            <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', margin: 0 }}>
                              {report.missing_skills?.map((gap, idx) => <li key={idx} style={{ marginBottom: '0.25rem' }}>{gap}</li>) || <li>No gaps identified.</li>}
                            </ul>
                          </div>

                          <div>
                            <h4 style={{ fontSize: 'var(--font-size-sm)', marginBottom: '0.25rem' }}>Summary Overview</h4>
                            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.6 }}>
                              {report.summary}
                            </p>
                          </div>

                          {report.recommendation && (
                            <div style={{ background: 'var(--color-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--color-accent-light)' }}>
                              <h4 style={{ fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                                Recommendation
                              </h4>
                              <p style={{ fontSize: 'var(--font-size-sm)', margin: 0, fontStyle: 'italic' }}>
                                "{report.recommendation}"
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </>
                ) : (
                  <div className="empty-state" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                      No Fit Score generated yet. Click "Generate Fit Score" to evaluate the candidate profile.
                    </p>
                  </div>
                )}

              </div>

            </div>

            {/* Scrollable extracted raw resume text section */}
            {selectedCandidate.parsed_resume && (
              <div style={{ marginTop: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1.25rem' }}>
                <h3 style={{ fontSize: 'var(--font-size-base)', marginBottom: '0.5rem' }}>Extracted Plain Document Text</h3>
                <pre style={{ background: 'var(--color-surface)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', fontSize: 'var(--font-size-xs)', maxHeight: '200px', overflowY: 'auto', whiteSpace: 'pre-wrap', color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>
                  {selectedCandidate.parsed_resume}
                </pre>
              </div>
            )}

            {/* Modal Actions Footer */}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', borderTop: '1px solid var(--color-border)', paddingTop: '1.25rem', marginTop: '1rem' }}>
              <button 
                className="btn btn-secondary" 
                onClick={() => { setSelectedCandidate(null); navigate(`/candidates/${selectedCandidate.id}/edit`); }}
              >
                Edit Profile
              </button>
              <button 
                className="btn btn-danger" 
                onClick={() => handleDelete(selectedCandidate.id)}
              >
                Delete Candidate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
