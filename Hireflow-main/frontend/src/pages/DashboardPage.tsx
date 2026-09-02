import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { jobsService } from '../services/jobs';
import type { Job, Candidate } from '../types';

interface DashboardStats {
  total_jobs: number;
  open_jobs: number;
  closed_jobs: number;
  total_candidates: number;
  avg_fit_score: number;
  highest_fit_score: number;
  recent_jobs: Job[];
  recent_candidates: Candidate[];
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    jobsService.getDashboardStats()
      .then(res => {
        setStats(res);
        setLoading(false);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to retrieve dashboard metrics');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="page-shell"><div className="loading-state">Loading dashboard stats…</div></div>;
  }

  if (error) {
    return <div className="page-shell"><div className="alert alert-error">{error}</div></div>;
  }

  if (!stats) return null;

  return (
    <div className="page-shell">
      {/* Friendly Greeting Hero Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #4f46e5 0%, #818cf8 100%)',
        color: '#ffffff',
        borderRadius: 'var(--radius-xl)',
        padding: '2.5rem',
        marginBottom: '2.5rem',
        boxShadow: 'var(--shadow-md)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'relative', zIndex: 2 }}>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, margin: 0, letterSpacing: '-0.025em', color: '#ffffff' }}>
            Welcome back, Anurag Singh! 👋
          </h1>
          <p style={{ opacity: 0.9, marginTop: '0.5rem', fontSize: '1.1rem', fontWeight: 500 }}>
            Here is your simple hiring overview. What would you like to do next?
          </p>
          
          {/* Main Quick Action Big Buttons */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', marginTop: '2rem' }}>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/jobs/new')}
              style={{
                background: '#ffffff',
                color: '#4f46e5',
                border: 'none',
                padding: '1rem 2rem',
                fontSize: '1.1rem',
                fontWeight: 700,
                borderRadius: 'var(--radius-lg)',
                boxShadow: '0 4px 14px rgba(0, 0, 0, 0.1)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
              onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
            >
              💼 Post a Job Opening
            </button>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/candidates/new')}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                color: '#ffffff',
                border: '1px solid rgba(255, 255, 255, 0.4)',
                padding: '1rem 2rem',
                fontSize: '1.1rem',
                fontWeight: 700,
                borderRadius: 'var(--radius-lg)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backdropFilter: 'blur(4px)',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
              onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
            >
              ⚡ Quick-Parse Resume
            </button>
          </div>
        </div>
        <div style={{
          position: 'absolute',
          right: '-50px',
          bottom: '-50px',
          width: '250px',
          height: '250px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '50%',
          zIndex: 1
        }}></div>
      </div>

      {/* Analytics Summary */}
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem', color: 'var(--color-text-primary)' }}>
        Your Pipeline Stats
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        {/* Total Candidates Card */}
        <div className="detail-card" style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ fontSize: '2.5rem', background: '#e0f2fe', width: '64px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>
            👥
          </div>
          <div>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'block', fontWeight: 500 }}>
              Total Applicants
            </span>
            <strong style={{ fontSize: '2rem', color: 'var(--color-text-primary)', fontWeight: 800 }}>
              {stats.total_candidates}
            </strong>
          </div>
        </div>

        {/* Avg Match Score Card */}
        <div className="detail-card" style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ fontSize: '2.5rem', background: '#fef3c7', width: '64px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>
            🎯
          </div>
          <div>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'block', fontWeight: 500 }}>
              Avg Match Score
            </span>
            <strong style={{ fontSize: '2rem', color: stats.avg_fit_score >= 80 ? 'var(--color-success)' : stats.avg_fit_score >= 60 ? 'var(--color-warning)' : 'var(--color-error)', fontWeight: 800 }}>
              {stats.avg_fit_score}%
            </strong>
          </div>
        </div>

        {/* Highest Score Card */}
        <div className="detail-card" style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ fontSize: '2.5rem', background: '#d1fae5', width: '64px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>
            🌟
          </div>
          <div>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'block', fontWeight: 500 }}>
              Top Match
            </span>
            <strong style={{ fontSize: '2rem', color: 'var(--color-success)', fontWeight: 800 }}>
              {stats.highest_fit_score}%
            </strong>
          </div>
        </div>

        {/* Jobs Card */}
        <div className="detail-card" style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ fontSize: '2.5rem', background: '#f3e8ff', width: '64px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>
            💼
          </div>
          <div>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'block', fontWeight: 500 }}>
              Active Jobs
            </span>
            <strong style={{ fontSize: '2rem', color: 'var(--color-text-primary)', fontWeight: 800 }}>
              {stats.open_jobs} <span style={{ fontSize: '0.9rem', fontWeight: 400, color: 'var(--color-text-secondary)' }}>/ {stats.total_jobs}</span>
            </strong>
          </div>
        </div>
      </div>

      {/* Two Column Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2.5rem' }}>
        {/* Left Column: Recent Candidates */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>Recent Candidates</h2>
            <Link to="/candidates" style={{ fontSize: '0.875rem', color: 'var(--color-accent)', fontWeight: 600 }}>
              View All →
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {stats.recent_candidates.length === 0 ? (
              <div className="empty-state" style={{ padding: '3rem', textAlign: 'center', background: '#ffffff', border: '1px dashed var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
                No candidates added yet. Upload a resume to get started!
              </div>
            ) : (
              stats.recent_candidates.map(cand => (
                <div 
                  key={cand.id} 
                  className="job-card" 
                  onClick={() => navigate('/candidates')}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem', cursor: 'pointer', background: '#ffffff', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', transition: 'transform 0.15s, box-shadow 0.15s' }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                  }}
                >
                  <div>
                    <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>{cand.name}</h4>
                    <span style={{ fontSize: '0.825rem', color: 'var(--color-text-secondary)', display: 'block', marginTop: '0.25rem' }}>
                      {cand.email}
                    </span>
                  </div>
                  {cand.fit_score !== null && (
                    <span className="skill-tag" style={{ background: '#e0f2fe', color: '#0369a1', border: 'none', fontWeight: 700, padding: '0.4rem 0.8rem', borderRadius: 'var(--radius-full)', fontSize: '0.825rem' }}>
                      🎯 {cand.fit_score}% match
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Recent Jobs */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>Recent Jobs</h2>
            <Link to="/jobs" style={{ fontSize: '0.875rem', color: 'var(--color-accent)', fontWeight: 600 }}>
              View All →
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {stats.recent_jobs.length === 0 ? (
              <div className="empty-state" style={{ padding: '3rem', textAlign: 'center', background: '#ffffff', border: '1px dashed var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
                No job openings created yet. Create one to begin matching!
              </div>
            ) : (
              stats.recent_jobs.map(job => (
                <div 
                  key={job.id} 
                  className="job-card" 
                  onClick={() => navigate(`/jobs/${job.id}`)}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem', cursor: 'pointer', background: '#ffffff', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', transition: 'transform 0.15s, box-shadow 0.15s' }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                  }}
                >
                  <div>
                    <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>{job.title}</h4>
                    <span style={{ fontSize: '0.825rem', color: 'var(--color-text-secondary)', display: 'block', marginTop: '0.25rem' }}>
                      📍 {job.location} · ⏱️ {job.employment_type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className={`badge badge-${job.status.toLowerCase()}`} style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', fontWeight: 700 }}>
                    {job.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
