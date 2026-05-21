import './ConfidenceDonut.css';

export default function ConfidenceDonut({ value = 0 }) {
  // value is 0-100
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(100, Math.max(0, value));
  const offset = circumference - (pct / 100) * circumference;

  const color =
    pct >= 85 ? 'hsl(150,65%,48%)' :
    pct >= 60 ? 'hsl(42,90%,58%)' :
    'hsl(0,70%,58%)';

  return (
    <div className="donut-wrapper">
      <svg className="donut-svg" viewBox="0 0 120 120" fill="none">
        {/* Track */}
        <circle
          cx="60" cy="60" r={radius}
          stroke="var(--border)" strokeWidth="10"
          fill="none"
        />
        {/* Progress */}
        <circle
          cx="60" cy="60" r={radius}
          stroke={color} strokeWidth="10"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16,1,0.3,1), stroke 0.4s' }}
        />
        {/* Glow filter */}
        <defs>
          <filter id="donut-glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <circle
          cx="60" cy="60" r={radius}
          stroke={color} strokeWidth="6"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
          filter="url(#donut-glow)"
          opacity="0.4"
        />
      </svg>

      <div className="donut-center">
        <span className="donut-value" style={{ color }}>{Math.round(pct)}</span>
        <span className="donut-unit">%</span>
        <span className="donut-label">Confidence</span>
      </div>
    </div>
  );
}
