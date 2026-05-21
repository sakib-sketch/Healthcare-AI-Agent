import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const [mode, setMode] = useState('login'); // 'login' | 'register' | 'reset'
  const [form, setForm] = useState({ name: '', email: '', password: '', newPassword: '' });
  const [msg, setMsg] = useState(null); // { type: 'success'|'error', text: string }
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';

  const update = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);

    if (mode === 'login') {
      const res = await login(form.email, form.password);
      if (res.success) navigate(from, { replace: true });
      else setMsg({ type: 'error', text: res.message });

    } else if (mode === 'register') {
      if (!form.name || !form.email || !form.password)
        return setMsg({ type: 'error', text: 'All fields are required.' });
      const res = await register(form.name, form.email, form.password);
      if (res.success) {
        setMsg({ type: 'success', text: 'Account created! Please log in.' });
        setMode('login');
      } else setMsg({ type: 'error', text: res.message });

    } else if (mode === 'reset') {
      if (!form.email || !form.newPassword)
        return setMsg({ type: 'error', text: 'Email and new password required.' });
      try {
        const axios = (await import('axios')).default;
        await axios.post('/api/auth/reset-password', { email: form.email, new_password: form.newPassword });
        setMsg({ type: 'success', text: 'Password reset successfully.' });
        setMode('login');
      } catch (err) {
        setMsg({ type: 'error', text: err.response?.data?.detail || 'Reset failed.' });
      }
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-orb orb-1" />
      <div className="auth-bg-orb orb-2" />

      <div className="auth-card glass fade-up">
        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <circle cx="20" cy="20" r="19" stroke="url(#g1)" strokeWidth="2"/>
              <path d="M20 10v20M10 20h20" stroke="url(#g2)" strokeWidth="3" strokeLinecap="round"/>
              <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="40" y2="40">
                  <stop stopColor="hsl(258,80%,65%)"/>
                  <stop offset="1" stopColor="hsl(210,90%,58%)"/>
                </linearGradient>
                <linearGradient id="g2" x1="0" y1="0" x2="40" y2="40">
                  <stop stopColor="hsl(258,80%,65%)"/>
                  <stop offset="1" stopColor="hsl(175,70%,50%)"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1 className="auth-brand">MediCode AI</h1>
            <p className="auth-tagline">Clinical Intelligence Platform</p>
          </div>
        </div>

        {/* Mode Tabs */}
        <div className="auth-tabs">
          {['login', 'register', 'reset'].map(m => (
            <button
              key={m}
              id={`auth-tab-${m}`}
              className={`auth-tab ${mode === m ? 'active' : ''}`}
              onClick={() => { setMode(m); setMsg(null); }}
            >
              {m === 'login' ? 'Sign In' : m === 'register' ? 'Register' : 'Reset'}
            </button>
          ))}
        </div>

        {/* Message */}
        {msg && (
          <div className={`auth-msg auth-msg-${msg.type}`}>
            {msg.type === 'error' ? '⚠' : '✓'} {msg.text}
          </div>
        )}

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className="auth-field">
              <label htmlFor="auth-name">Full Name</label>
              <input id="auth-name" type="text" placeholder="Dr. Jane Smith" value={form.name} onChange={update('name')} required />
            </div>
          )}
          <div className="auth-field">
            <label htmlFor="auth-email">Email Address</label>
            <input id="auth-email" type="email" placeholder="doctor@hospital.com" value={form.email} onChange={update('email')} required />
          </div>
          {mode !== 'reset' && (
            <div className="auth-field">
              <label htmlFor="auth-password">Password</label>
              <input id="auth-password" type="password" placeholder="••••••••" value={form.password} onChange={update('password')} required />
            </div>
          )}
          {mode === 'reset' && (
            <div className="auth-field">
              <label htmlFor="auth-new-password">New Password</label>
              <input id="auth-new-password" type="password" placeholder="New secure password" value={form.newPassword} onChange={update('newPassword')} required />
            </div>
          )}
          <button id="auth-submit-btn" type="submit" className="btn-primary auth-submit" disabled={loading}>
            {loading ? <span className="spin" style={{display:'inline-block',width:16,height:16,border:'2px solid #fff4',borderTopColor:'#fff',borderRadius:'50%'}}></span> : null}
            {mode === 'login' ? 'Sign In' : mode === 'register' ? 'Create Account' : 'Reset Password'}
          </button>
        </form>

        <p className="auth-footer">
          Secure · HIPAA-conscious · End-to-end encrypted
        </p>
      </div>
    </div>
  );
}
