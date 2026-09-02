import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { 
  LoginPage, 
  RegisterPage, 
  JobListPage, 
  JobFormPage, 
  JobDetailPage, 
  CandidateListPage, 
  CandidateFormPage,
  DashboardPage
} from './pages';

function NavBar({ userName, onLogout }: { userName: string; onLogout: () => void }) {
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <Link to="/" className="nav-brand">Gappeo Recruiter</Link>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/" style={{ color: 'var(--color-text)', textDecoration: 'none', fontWeight: 600 }}>Dashboard</Link>
          <Link to="/jobs" style={{ color: 'var(--color-text)', textDecoration: 'none', fontWeight: 600 }}>Jobs</Link>
          <Link to="/candidates" style={{ color: 'var(--color-text)', textDecoration: 'none', fontWeight: 600 }}>Candidates</Link>
        </div>
      </div>
      <div className="nav-right">
        <span className="nav-user">{userName}</span>
        <button className="btn btn-secondary btn-sm" onClick={() => { onLogout(); navigate('/'); }}>Sign Out</button>
      </div>
    </nav>
  );
}

function AuthenticatedApp({ userName, onLogout }: { userName: string; onLogout: () => void }) {
  return (
    <>
      <NavBar userName={userName} onLogout={onLogout} />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/jobs" element={<JobListPage />} />
        <Route path="/jobs/new" element={<JobFormPage mode="create" />} />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
        <Route path="/jobs/:id/edit" element={<JobFormPage mode="edit" />} />
        <Route path="/candidates" element={<CandidateListPage />} />
        <Route path="/candidates/new" element={<CandidateFormPage mode="create" />} />
        <Route path="/candidates/:id/edit" element={<CandidateFormPage mode="edit" />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

function UnauthenticatedApp({ onLogin, onRegister }: { onLogin: (e: string, p: string) => Promise<void>; onRegister: (n: string, e: string, p: string) => Promise<void> }) {
  const [view, setView] = useState<'login' | 'register'>('login');
  return (
    <Routes>
      <Route path="*" element={
        view === 'login'
          ? <LoginPage onLogin={onLogin} onSwitchToRegister={() => setView('register')} />
          : <RegisterPage onRegister={onRegister} onSwitchToLogin={() => setView('login')} />
      } />
    </Routes>
  );
}

function App() {
  const { user, isAuthenticated, isLoading, login, register, logout } = useAuth();

  if (isLoading) {
    return <div className="page-container"><div className="loading-state">Loading…</div></div>;
  }

  return (
    <BrowserRouter>
      {isAuthenticated && user
        ? <AuthenticatedApp userName={user.name} onLogout={logout} />
        : <UnauthenticatedApp onLogin={login} onRegister={register} />
      }
    </BrowserRouter>
  );
}

export default App;
