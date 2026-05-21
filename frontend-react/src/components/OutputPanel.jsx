import axios from 'axios';
import ConfidenceDonut from './ConfidenceDonut';
import EntitiesShowcase from './EntitiesShowcase';
import './OutputPanel.css';

const STATUS_TAG = {
  Confirmed: 'tag-ok',
  Valid: 'tag-ok',
  Flagged: 'tag-warn',
  Warning: 'tag-warn',
  Rejected: 'tag-err',
  Error: 'tag-err',
};

export default function OutputPanel({ result, isLoading }) {
  if (isLoading) {
    return (
      <div className="output-panel glass loading-state">
        <div className="loading-spinner" />
        <p className="loading-text">Running multi-agent pipeline…</p>
        <p className="loading-sub">Extracting → Coding → Auditing → Reporting → Summarizing</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="output-panel glass empty-state">
        <div className="empty-icon">🏥</div>
        <h3 className="empty-title">No Analysis Yet</h3>
        <p className="empty-sub">Paste a clinical note and click <strong>Run Analysis</strong> to get started.</p>
      </div>
    );
  }

  const { summary = {}, details = [], patient_summary = '', case_id } = result;
  const confidence = summary.confidence_score ?? summary.avg_confidence ?? 0;
  const totalBill = summary.total_revenue ?? summary.total_bill ?? 0;

  // Build entities from details
  const entities = details.map(d => ({
    entity_text: d.entity || d.diagnosis || '',
    entity_type: d.type || 'Diagnosis',
  })).filter(e => e.entity_text);

  const handleDownload = () => {
    if (case_id) {
      window.open(`/api/reports/bill/${case_id}`, '_blank');
    }
  };

  return (
    <div className="output-panel glass fade-up">
      {/* Header bar */}
      <div className="output-header">
        <h3 className="panel-title">Analysis Results</h3>
        <div className="output-actions">
          {case_id && (
            <button id="download-invoice-btn" className="btn-ghost" onClick={handleDownload}>
              ⬇ Invoice PDF
            </button>
          )}
          <span className="case-id-badge">
            {case_id ? `Case #${case_id}` : 'Unsaved'}
          </span>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="output-body">
        {/* Metrics row */}
        <div className="metrics-row">
          <ConfidenceDonut value={confidence} />

          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-value">{summary.total_diagnoses ?? 0}</span>
              <span className="metric-label">Diagnoses</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{summary.total_codes ?? 0}</span>
              <span className="metric-label">Codes Mapped</span>
            </div>
            <div className="metric-card">
              <span className="metric-value green">${Number(totalBill).toFixed(2)}</span>
              <span className="metric-label">Total Bill</span>
            </div>
            <div className="metric-card">
              <span className="metric-value amber">{details.filter(d => d.status === 'Flagged' || d.status === 'Warning').length}</span>
              <span className="metric-label">Flags</span>
            </div>
          </div>
        </div>

        {/* Patient summary */}
        {patient_summary && (
          <div className="patient-summary-block">
            <div className="section-label">💬 Patient-Friendly Summary</div>
            <p className="patient-summary-text">{patient_summary}</p>
          </div>
        )}

        {/* Clinical entities */}
        {entities.length > 0 && (
          <div className="section-block">
            <div className="section-label">🔬 Clinical Entities</div>
            <EntitiesShowcase entities={entities} />
          </div>
        )}

        {/* ICD-10 Billing Table */}
        {details.length > 0 && (
          <div className="section-block table-section">
            <div className="section-label">🏷️ ICD-10 / CPT Billing Table</div>
            <div className="table-scroll">
              <table className="billing-table">
                <thead>
                  <tr>
                    <th>Diagnosis / Entity</th>
                    <th>Code</th>
                    <th>CPT Code</th>
                    <th>Fee</th>
                    <th>Confidence</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {details.map((row, i) => {
                    const diagName = row.entity || row.diagnosis || '—';
                    const icdCode  = row.code || row.icd10_code || '—';
                    const cptCode  = row.cpt_code || '—';
                    const fee      = row.fee != null ? `$${Number(row.fee).toFixed(2)}` : '—';
                    const conf     = row.confidence != null ? `${(Number(row.confidence) * 100).toFixed(0)}%` : '—';
                    const status   = row.status || 'Valid';
                    const tagCls   = STATUS_TAG[status] || 'tag-info';

                    return (
                      <tr key={i} className={i % 2 === 0 ? 'row-even' : ''}>
                        <td className="diag-cell">{diagName}</td>
                        <td><span className="mono code-badge">{icdCode}</span></td>
                        <td><span className="mono code-badge secondary">{cptCode}</span></td>
                        <td className="fee-cell">{fee}</td>
                        <td className="conf-cell">{conf}</td>
                        <td><span className={`tag ${tagCls}`}>{status}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
