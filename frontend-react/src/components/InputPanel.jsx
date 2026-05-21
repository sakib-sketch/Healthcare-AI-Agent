import { useState, useRef } from 'react';
import axios from 'axios';
import './InputPanel.css';

const DEMO_NOTES = {
  cardiology: `Patient: John D., 67M. Chief complaint: chest pain and dyspnea on exertion for 3 days.
PMH: Hypertension, Type 2 DM, hyperlipidemia.
Assessment: Unstable angina (I20.0), essential hypertension (I10), and type 2 diabetes mellitus (E11.9).
Procedure: Coronary angiography performed (CPT 93454). EKG done.
Plan: Admit to CCU, start heparin infusion, cardiology consult.`,
  respiratory: `Patient: Sarah M., 52F. Acute exacerbation of COPD (J44.1).
Presenting with increased dyspnea, productive cough with green sputum, and wheezing.
SpO2 88% on room air. CXR: hyperinflation, no consolidation.
Treatment: Nebulised salbutamol, ipratropium, IV hydrocortisone, oxygen therapy.
Procedure: Pulmonary function test (CPT 94010).`,
  diabetes: `Patient: Michael R., 44M. Poorly controlled type 2 diabetes (E11.65).
HbA1c: 11.2%. Recent hypoglycaemic episodes on glipizide.
Complications: Diabetic peripheral neuropathy (E11.40), background diabetic retinopathy (E11.319).
Procedure: Comprehensive metabolic panel (CPT 80053), HbA1c (CPT 83036).
Plan: Adjust medications, refer to endocrinology.`,
};

export default function InputPanel({ onAnalyze, isLoading }) {
  const [tab, setTab] = useState('text'); // 'text' | 'upload' | 'audio'
  const [noteText, setNoteText] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  // Audio recording state
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioStatus, setAudioStatus] = useState('');
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // ---- Demo loaders ----
  const loadDemo = (key) => {
    setNoteText(DEMO_NOTES[key]);
    setTab('text');
  };

  // ---- File Upload ----
  const processFile = async (file) => {
    if (!file) return;
    setUploadStatus({ type: 'loading', text: `Extracting text from ${file.name}…` });
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await axios.post('/api/process/document', fd);
      setNoteText(res.data.text);
      setUploadStatus({ type: 'success', text: `✓ Extracted from ${file.name}` });
      setTab('text');
    } catch (e) {
      setUploadStatus({ type: 'error', text: e.response?.data?.detail || 'Extraction failed.' });
    }
  };

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false);
    processFile(e.dataTransfer.files[0]);
  };

  // ---- Audio Recording ----
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioStatus('Transcribing via Google Speech…');
        const fd = new FormData();
        fd.append('file', blob, 'recording.webm');
        try {
          const res = await axios.post('/api/process/audio', fd);
          setNoteText(res.data.text);
          setAudioStatus('✓ Transcription complete');
          setTab('text');
        } catch {
          setAudioStatus('Transcription failed — paste text manually.');
        }
      };
      mediaRecorderRef.current = mr;
      mr.start();
      setRecording(true);
      setAudioStatus('🎙 Recording…');
    } catch {
      setAudioStatus('Microphone access denied.');
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const handleAnalyze = () => {
    if (noteText.trim()) onAnalyze(noteText.trim());
  };

  return (
    <div className="input-panel glass">
      <div className="panel-header">
        <h3 className="panel-title">Clinical Note Input</h3>
        <div className="demo-pills">
          {Object.keys(DEMO_NOTES).map(k => (
            <button key={k} id={`demo-${k}`} className="demo-pill" onClick={() => loadDemo(k)}>
              {k.charAt(0).toUpperCase() + k.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Input Tabs */}
      <div className="input-tabs">
        {['text','upload','audio'].map(t => (
          <button
            key={t}
            id={`input-tab-${t}`}
            className={`input-tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t === 'text' ? '📝 Text' : t === 'upload' ? '📎 Upload' : '🎙 Audio'}
          </button>
        ))}
      </div>

      {/* Text Tab */}
      {tab === 'text' && (
        <textarea
          id="clinical-note-textarea"
          className="note-textarea"
          placeholder="Paste or type the clinical note here…"
          value={noteText}
          onChange={e => setNoteText(e.target.value)}
          rows={12}
        />
      )}

      {/* Upload Tab */}
      {tab === 'upload' && (
        <div
          className={`dropzone ${dragOver ? 'drag-over' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".txt,.pdf,.docx"
            style={{ display: 'none' }}
            onChange={e => processFile(e.target.files[0])}
          />
          <div className="dropzone-icon">📂</div>
          <p className="dropzone-text">Drop a file here or click to browse</p>
          <p className="dropzone-sub">Supports PDF · DOCX · TXT</p>
          {uploadStatus && (
            <p className={`upload-status ${uploadStatus.type}`}>{uploadStatus.text}</p>
          )}
        </div>
      )}

      {/* Audio Tab */}
      {tab === 'audio' && (
        <div className="audio-section">
          <div className="audio-visualizer">
            {recording && Array.from({length: 20}).map((_, i) => (
              <div key={i} className="audio-bar" style={{ animationDelay: `${i * 0.05}s` }} />
            ))}
            {!recording && <div className="audio-idle-icon">🎙</div>}
          </div>
          <button
            id="record-btn"
            className={`btn-primary ${recording ? 'recording' : ''}`}
            onClick={recording ? stopRecording : startRecording}
          >
            {recording ? '⏹ Stop Recording' : '● Start Recording'}
          </button>
          {audioStatus && <p className="audio-status">{audioStatus}</p>}
        </div>
      )}

      {/* Char count & Analyze */}
      <div className="input-footer">
        <span className="char-count">{noteText.length} characters</span>
        <button
          id="analyze-btn"
          className="btn-primary analyze-btn"
          onClick={handleAnalyze}
          disabled={isLoading || !noteText.trim()}
        >
          {isLoading
            ? <><span className="spin" style={{display:'inline-block',width:14,height:14,border:'2px solid #fff3',borderTopColor:'#fff',borderRadius:'50%'}}></span> Analyzing…</>
            : '⚡ Run Analysis'}
        </button>
      </div>
    </div>
  );
}
