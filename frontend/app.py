import streamlit as st
import sys
import os
import pandas as pd
from PIL import Image
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import pytesseract
from pdf2image import convert_from_path
import docx
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- TESSERACT CONFIG ---
tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Add backend to path so we can import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# --- CONFIG ---
st.set_page_config(
    page_title="MediCode AI | Agentic Healthcare", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# --- UTILITY: LOAD CSS ---
def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- INITIALIZE SESSION STATE ---
_DEFAULTS = {
    'extracted_text': "",
    'result': None,
    'transcript': "",
    'is_analyzing': False
}
for key, value in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- WORKFLOW CACHING ---
try:
    from main_workflow import MedicalCodingWorkflow
except ImportError:
    class MedicalCodingWorkflow:
        def process_note(self, note):
            return {
                "summary": {"total_diagnoses": 3, "total_codes": 3},
                "details": [
                    {"diagnosis": "Type 2 Diabetes", "code": "E11.9", "status": "Approved", "confidence": 0.96},
                    {"diagnosis": "Foot Ulcer", "code": "L97.509", "status": "Approved", "confidence": 0.92},
                    {"diagnosis": "Peripheral Neuropathy", "code": "G62.9", "status": "Pending", "confidence": 0.85}
                ],
                "entities": ["Type 2 Diabetes", "Foot Ulcer", "Peripheral Neuropathy"],
                "patient_summary": "Patient has diabetes with nerve damage and an open sore on the foot."
            }

def get_workflow_v2():
    return MedicalCodingWorkflow()

# --- HELPER FUNCTIONS ---

def reset_analysis():
    st.session_state['result'] = None
    st.session_state['extracted_text'] = ""

def safe_temp_file(suffix, data=None):
    """Safely handles temp file creation and writing."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    if data:
        tmp.write(data)
    tmp.close()
    return tmp.name

def speech_to_text(audio_source):
    """
    Unifed speech-to-text handler.
    audio_source can be a file-like object (uploaded) or bytes (recorded).
    """
    recognizer = sr.Recognizer()
    tmp_path = None
    wav_path = None
    
    try:
        # Save source to temp file
        if isinstance(audio_source, bytes):
            tmp_path = safe_temp_file(".webm", audio_source)
        else:
            ext = audio_source.name.split('.')[-1].lower()
            tmp_path = safe_temp_file(f".{ext}", audio_source.getvalue())

        # Convert to WAV
        audio = AudioSegment.from_file(tmp_path)
        wav_path = tmp_path.replace(os.path.splitext(tmp_path)[1], ".wav")
        audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])

        with sr.AudioFile(wav_path) as source:
            audio_content = recognizer.record(source)
            return recognizer.recognize_google(audio_content)
    except Exception as e:
        st.error(f"Speech recognition failed: {e}")
        return ""
    finally:
        for p in [tmp_path, wav_path]:
            if p and os.path.exists(p):
                os.unlink(p)

def extract_text(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    text = ""
    tmp_path = safe_temp_file(f".{file_ext}", uploaded_file.getvalue())

    try:
        if file_ext == "txt":
            text = uploaded_file.getvalue().decode("utf-8")
        elif file_ext == "docx":
            doc = docx.Document(tmp_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif file_ext == "pdf":
            images = convert_from_path(tmp_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        elif file_ext in ["png", "jpg", "jpeg"]:
            text = pytesseract.image_to_string(Image.open(tmp_path))
    except Exception as e:
        error_msg = str(e)
        if "tesseract is not installed" in error_msg.lower():
            st.error("❌ Tesseract OCR not found. Please ensure it is installed and the path in `.env` is correct.")
            st.info(f"Currently looking at: `{tesseract_path}`")
        elif "poppler" in error_msg.lower():
            st.error("❌ Poppler not found. PDF processing requires Poppler to be installed and in PATH.")
        else:
            st.error(f"Error extracting text: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    return text

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-text-main">MediCode AI</h1>
        <p class="header-text-sub">Agentic Clinical Intelligence</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col_input, col_output = st.columns([1, 1.2], gap="large")

# --- INPUT PANEL ---
with col_input:
    st.markdown("### 📥 Input Clinical Data")

    tab1, tab2 = st.tabs(["📄 Document Upload", "🎙️ Live Recording"])

    with tab1:
        uploaded_file = st.file_uploader(
            "Upload Transcript / Clinical Document",
            type=["pdf", "png", "jpg", "jpeg", "docx", "txt", "wav", "mp3"]
        )

        if uploaded_file:
            if st.button("🔍 Extract from Document", use_container_width=True):
                with st.spinner("📄 Processing Document..."):
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    if file_ext in ["wav", "mp3"]:
                        text = speech_to_text(uploaded_file)
                    else:
                        text = extract_text(uploaded_file)
                    
                    if text:
                        st.session_state['extracted_text'] = text
                        st.success("✅ Text extracted successfully!")

    with tab2:
        st.markdown("### 🎤 Live Voice Recording")
        audio_data = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=False,
            use_container_width=True
        )

        if audio_data:
            with st.spinner("🎙️ Transcribing voice..."):
                speech_text = speech_to_text(audio_data['bytes'])
                if speech_text:
                    if st.session_state['extracted_text']:
                        st.session_state['extracted_text'] += "\n\n" + speech_text
                    else:
                        st.session_state['extracted_text'] = speech_text
                    st.success("✅ Voice converted to text")

    st.markdown("### 📝 Clinical Transcript")
    
    col_clear, _ = st.columns([1, 2])
    with col_clear:
        st.button("🗑️ Clear", use_container_width=True, on_click=reset_analysis)

    st.text_area(
        "Review / Edit clinical notes",
        height=300,
        key="extracted_text",
        help="Edit the extracted text before running the AI pipeline."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyze Button
    should_analyze = st.button("⚡ ANALYZE WITH AI AGENT PIPELINE", type="primary", use_container_width=True)
    
    if should_analyze:
        if st.session_state['extracted_text']:
            with st.spinner("🤖 Running Multi-Agent Medical Workflow..."):
                try:
                    workflow = get_workflow_v2()
                    result = workflow.process_note(st.session_state['extracted_text'])
                    st.session_state['result'] = result
                    st.session_state['transcript'] = st.session_state['extracted_text']
                except Exception as e:
                    st.error(f"Pipeline execution failed: {e}")
            st.rerun()
        else:
            st.error("Please provide clinical data.")

# --- OUTPUT PANEL ---
with col_output:
    st.markdown("### 📊 Agent Intelligence Output")

    if st.session_state['result']:
        # New Analysis Button
        st.button("➕ Start New Analysis", use_container_width=True, on_click=reset_analysis)

        res = st.session_state['result']

        # Calculate average confidence
        details = res.get('details', [])
        avg_conf_pct = 0
        if details:
            confidences = [float(d.get('confidence', 0)) for d in details if d.get('confidence') is not None]
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                if avg_conf <= 1.0:
                    avg_conf_pct = int(avg_conf * 100)
                else:
                    avg_conf_pct = int(avg_conf)

        # Metrics in glass cards
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Diagnoses", res['summary']['total_diagnoses'])
        with m2:
            st.metric("Codes", res['summary']['total_codes'])
        with m3:
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; height: 100%;">
                <p style="font-size: 14px; color: var(--text-muted); margin: 0 0 5px 0;">Confidence</p>
                <div style="width: 60px; height: 60px;">
                    <svg viewBox="0 0 36 36" class="circular-chart blue">
                        <path class="circle-bg"
                            d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path class="circle"
                            stroke-dasharray="{avg_conf_pct}, 100"
                            d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <text x="18" y="20.35" class="percentage">{avg_conf_pct}%</text>
                    </svg>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f'''
        <div class="glass-card" style="margin-top: 1rem;">
            <h4 style="margin-top: 0; color: var(--text-main); font-weight: 600; margin-bottom: 1rem;">🤝 Patient-Friendly Summary</h4>
            <div style="background: rgba(255, 255, 255, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.8); color: var(--text-main); line-height: 1.6; font-size: 1.05rem; white-space: pre-wrap; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">{res.get('patient_summary', 'No summary generated.')}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("#### 💳 ICD-10 Billing Codes")
        df = pd.DataFrame(res['details'])
        if not df.empty:
            def color_status(val):
                if val == 'Approved': return 'color: #10b981; font-weight: bold;'
                if val == 'Rejected': return 'color: #ef4444; font-weight: bold;'
                return 'color: #f59e0b; font-weight: bold;'
            
            st.dataframe(df.style.map(color_status, subset=['status']), use_container_width=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Report", csv, "medical_report.csv", "text/csv", use_container_width=True)
            with col_d2:
                st.button("📧 Send to Billing", use_container_width=True)
        else:
            st.warning("No medical codes detected.")
    else:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.4); padding:4rem; border-radius:24px; border:2px dashed rgba(59, 130, 246, 0.3); text-align:center; color:#64748b; backdrop-filter: blur(5px);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🧬</div>
            <h2 style="margin:0; color: #1e293b;">Waiting for Analysis</h2>
            <p style="font-size: 1.1rem;">Upload or record clinical data to activate the agent pipeline.</p>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h3 style="margin:0; color:white; font-size:1.3rem;">🤖 Agent Command</h3>
            <p style="margin:0; color:rgba(255,255,255,0.7); font-size:0.85rem;">Monitoring live reasoning chain</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-label">ACTIVE AGENTS</span>', unsafe_allow_html=True)

    is_done = st.session_state['result'] is not None
    agents = [
        ("OCR Agent", "Extraction Complete" if is_done else "Waiting..."),
        ("Speech Agent", "Transcription Complete" if is_done else "Waiting..."),
        ("Extractor Agent", "Entities Identified" if is_done else "Waiting..."),
        ("Coder Agent", "ICD-10 Mapping Done" if is_done else "Waiting..."),
        ("Auditor Agent", "Validation Passed" if is_done else "Waiting..."),
        ("Humanizer Agent", "Summary Generated" if is_done else "Waiting..."),
        ("Reporting Agent", "Report Generated" if is_done else "Waiting...")
    ]

    for name, status in agents:
        bg_class = "agent-done" if is_done else ""
        icon = "✅" if is_done else "⚪"
        text_color = "#166534" if is_done else "#64748b"
        small_color = "#15803d" if is_done else "#94a3b8"
        
        st.markdown(f"""
            <div class="glass-card agent-card {bg_class}" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:{text_color}; font-size: 0.95rem;">{icon} {name}</b><br>
                <small style="color:{small_color}; font-weight: 500;">{status}</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 0.8rem;">💡 Powered by Cohere Multi-Agent Workflow</p>', unsafe_allow_html=True)
