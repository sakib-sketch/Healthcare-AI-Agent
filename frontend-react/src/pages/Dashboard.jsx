import { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import AgentCommandCenter from '../components/AgentCommandCenter';
import InputPanel from '../components/InputPanel';
import OutputPanel from '../components/OutputPanel';
import './Dashboard.css';

// Maps agent pipeline steps to sidebar index (0-indexed)
const STEP_KEYWORDS = ['Extract', 'Mapp', 'Audit', 'Report', 'summary', 'Saving'];

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [status, setStatus]       = useState('idle');   // idle | running | done | error
  const [activeStep, setActiveStep] = useState(-1);
  const [result, setResult]       = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg]   = useState('');

  const simulateSteps = (onDone) => {
    // Simulate progressive step advancement while the API is working
    let step = 0;
    const advance = () => {
      if (step < 5) {
        setActiveStep(step);
        step++;
        setTimeout(advance, 1800);
      }
    };
    advance();
  };

  const handleAnalyze = async (clinicalNote) => {
    setIsLoading(true);
    setStatus('running');
    setResult(null);
    setErrorMsg('');
    setActiveStep(0);
    simulateSteps();

    try {
      const res = await axios.post('/api/workflow/analyze', { clinical_note: clinicalNote });
      setResult(res.data.result);
      setStatus('done');
      setActiveStep(5); // mark all done
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-shell">
      {/* Top navbar */}
      <header className="dash-navbar glass">
        <div className="dash-brand">
          <div className="brand-dot" />
          <span className="brand-name">MediCode AI</span>
          <span className="brand-version">v2.0 React</span>
        </div>

        <div className="dash-status">
          {status === 'running' && (
            <span className="status-pill running">
              <span className="spin" style={{display:'inline-block',width:10,height:10,border:'1.5px solid #fff3',borderTopColor:'#fff',borderRadius:'50%'}} />
              Agents Running
            </span>
          )}
          {status === 'done' && (
            <span className="status-pill done">✓ Analysis Complete</span>
          )}
          {status === 'error' && (
            <span className="status-pill error">✕ {errorMsg}</span>
          )}
        </div>

        <div className="dash-user">
          <div className="user-avatar">{user?.name?.[0]?.toUpperCase() || 'U'}</div>
          <div className="user-info">
            <span className="user-name">{user?.name}</span>
            <span className="user-email">{user?.email}</span>
          </div>
          <button id="logout-btn" className="btn-ghost logout-btn" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      {/* Main workspace */}
      <main className="dash-workspace">
        {/* Left: Agent Console */}
        <AgentCommandCenter status={status} activeStep={activeStep} />

        {/* Center: Input Panel */}
        <div className="dash-center glass">
          <InputPanel onAnalyze={handleAnalyze} isLoading={isLoading} />
        </div>

        {/* Right: Output Panel */}
        <div className="dash-right glass">
          <OutputPanel result={result} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}
