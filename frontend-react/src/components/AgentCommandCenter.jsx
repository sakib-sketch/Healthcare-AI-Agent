import { useState, useEffect } from 'react';
import './AgentCommandCenter.css';

const AGENTS = [
  { id: 'extractor', label: 'Extractor Agent', icon: '🔍', desc: 'NLP entity extraction' },
  { id: 'coder',     label: 'Coder Agent',     icon: '🏷️', desc: 'ICD-10 / CPT mapping' },
  { id: 'auditor',   label: 'Auditor Agent',   icon: '🛡️', desc: 'Compliance audit' },
  { id: 'reporter',  label: 'Reporter Agent',  icon: '📋', desc: 'Report generation' },
  { id: 'humanizer', label: 'Humanizer Agent', icon: '💬', desc: 'Patient summary' },
  { id: 'database',  label: 'Database',        icon: '💾', desc: 'PostgreSQL persist' },
];

// step index -> agent id
const STEP_MAP = ['extractor','coder','auditor','reporter','humanizer','database'];

export default function AgentCommandCenter({ status, activeStep }) {
  // status: 'idle' | 'running' | 'done' | 'error'
  // activeStep: 0-5 (which agent is currently running)

  return (
    <aside className="acc-sidebar glass">
      <div className="acc-header">
        <div className="acc-logo-dot" />
        <h2 className="acc-title">Agent Console</h2>
        <span className={`tag ${status === 'running' ? 'tag-warn' : status === 'done' ? 'tag-ok' : status === 'error' ? 'tag-err' : 'tag-info'}`}>
          {status === 'running' ? 'Live' : status === 'done' ? 'Done' : status === 'error' ? 'Error' : 'Idle'}
        </span>
      </div>

      <div className="acc-timeline">
        {AGENTS.map((agent, idx) => {
          const isActive  = status === 'running' && activeStep === idx;
          const isDone    = status === 'done' || (status === 'running' && idx < activeStep);
          const isError   = status === 'error' && activeStep === idx;

          return (
            <div key={agent.id} className={`acc-step ${isActive ? 'active' : ''} ${isDone ? 'done' : ''} ${isError ? 'error' : ''}`}>
              {/* Connector line */}
              {idx < AGENTS.length - 1 && (
                <div className={`acc-connector ${isDone ? 'done' : ''}`} />
              )}

              <div className="acc-step-icon">
                {isActive ? <span className="spin" style={{display:'block',width:14,height:14,border:'2px solid #fff3',borderTopColor:'var(--accent-primary)',borderRadius:'50%'}} /> : agent.icon}
              </div>

              <div className="acc-step-info">
                <span className="acc-step-label">{agent.label}</span>
                <span className="acc-step-desc">{agent.desc}</span>
              </div>

              <div className="acc-step-status">
                {isActive && <span className="acc-dot pulse" />}
                {isDone && <span style={{color:'var(--status-ok)',fontSize:'0.85rem'}}>✓</span>}
                {isError && <span style={{color:'var(--status-err)',fontSize:'0.85rem'}}>✕</span>}
              </div>
            </div>
          );
        })}
      </div>

      <div className="acc-footer">
        <p className="acc-footer-text">Powered by Cohere Command R+</p>
        <div className="acc-model-badge">
          <span className="acc-model-dot" />
          cohere-r-plus
        </div>
      </div>
    </aside>
  );
}
