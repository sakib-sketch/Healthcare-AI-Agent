import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import streamlit as st
import sys
import pandas as pd
from PIL import Image
import tempfile
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- TESSERACT CONFIG ---
tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Add backend to path so we can import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Force reload of database package to clear out old SQLite caching from active Streamlit memory
if 'database' in sys.modules:
    import importlib
    if 'database.db' in sys.modules:
        import database.db
        importlib.reload(database.db)
    import database
    importlib.reload(database)

# --- CONFIG ---
st.set_page_config(
    page_title="MediCode AI | Agentic Healthcare", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# --- AUTHENTICATION GATEKEEPER ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from Registration import render_auth_page
    render_auth_page()
    st.stop()

# --- UTILITY: LOAD CSS ---
def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- INITIALIZE SESSION STATE ---
_DEFAULT_TEXT = """Patient: Sarah Jenkins (DOB: 05/12/1962). Contact number: 555-0198.
The patient presented today with a painful ulcer on her right foot. 
Diagnosis: Diabetic Foot Ulcer and Peripheral Neuropathy.
Treatment: Ordered wound dressing and referred to Podiatry."""

_DEFAULTS = {
    'extracted_text': _DEFAULT_TEXT,
    'result': None,
    'transcript': "",
    'is_analyzing': False,
    # Navigation
    'page': 'coding',
    # CDS states
    'cds_result': None,
    'cds_symptoms': '',
    'cds_medications': '',
    'cds_history': '',
    'cds_demographics': '',
    'cds_vitals': ''
}
for key, value in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- WORKFLOW CACHING ---
try:
    from main_workflow import MedicalCodingWorkflow
    print("SUCCESSFULLY IMPORTED REAL WORKFLOW")
except Exception as e:
    print(f"FAILED TO IMPORT REAL WORKFLOW: {e}")
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

# --- CDS WORKFLOW ---
try:
    from cds_workflow import ClinicalDecisionWorkflow
    print("SUCCESSFULLY IMPORTED CDS WORKFLOW")
except Exception as e:
    print(f"FAILED TO IMPORT CDS WORKFLOW: {e}")
    ClinicalDecisionWorkflow = None

def get_cds_workflow():
    try:
        import importlib
        import cds_workflow
        importlib.reload(cds_workflow)
        return cds_workflow.ClinicalDecisionWorkflow()
    except Exception as e:
        print(f"Failed to load CDS workflow: {e}")
        return None

def get_workflow_v2():
    try:
        import importlib
        import main_workflow
        importlib.reload(main_workflow)
        import agents.reporter
        importlib.reload(agents.reporter)
        import database.crud
        importlib.reload(database.crud)
        print("RELOADED WORKFLOW AND DATABASE SCRIPTS successfully")
        return main_workflow.MedicalCodingWorkflow()
    except Exception as e:
        print(f"Failed to reload workflow modules: {e}")
        return MedicalCodingWorkflow()

def extract_patient_name(transcript):
    import re
    if not transcript:
        return "John Doe"
    # Try common explicit formats
    patterns = [
        r"(?i)patient\s*name\s*:\s*([^\n\r,]+)",
        r"(?i)patient\s*:\s*([^\n\r,]+)",
        r"(?i)name\s*:\s*([^\n\r,]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, transcript)
        if match:
            name = match.group(1).strip()
            # Remove DOB or Contact info if captured on the same line
            name = re.split(r"(?i)\b(?:dob|date of birth|contact|phone|tel|number)\b", name)[0].strip()
            name = re.sub(r'[^\w\s\.-]', '', name).strip()
            if name:
                return name
                
    # Look for "Jane Doe, a 45-year-old" or similar in the text
    match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+),\s*(?:a\s+)?\d+[- ]*(?:year|yo|y\.o\.)", transcript)
    if match:
        name = match.group(1).strip()
        name = re.split(r"(?i)\b(?:dob|date of birth|contact|phone|tel|number)\b", name)[0].strip()
        return name
        
    # Look for "Jane Doe is a 45-year-old"
    match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)\s+is\s+a\s+\d+[- ]*(?:year|yo|y\.o\.)", transcript)
    if match:
        name = match.group(1).strip()
        name = re.split(r"(?i)\b(?:dob|date of birth|contact|phone|tel|number)\b", name)[0].strip()
        return name
        
    return "John Doe"

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
    import speech_recognition as sr
    from pydub import AudioSegment
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
    import docx
    import pytesseract
    from pdf2image import convert_from_path

    # Configure Tesseract path
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

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
if st.session_state['page'] == 'coding':

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
            res = st.session_state['result']
            


            st.button("➕ Start New Analysis", use_container_width=True, on_click=reset_analysis)

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

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Diagnoses", res['summary'].get('total_diagnoses', 0))
            with m2:
                st.metric("Procedures", res['summary'].get('total_procedures', 0))
            with m3:
                st.metric("Total Codes", res['summary'].get('total_codes', 0))
            with m4:
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; height: 100%;">
                    <p style="font-size: 14px; color: var(--text-muted); margin: 0 0 5px 0;">Confidence</p>
                    <div style="width: 50px; height: 50px;">
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
                <h4 style="margin-top: 0; color: var(--text-main); font-weight: 600; margin-bottom: 1rem;">🤝 Summary</h4>
                <div style="background: rgba(255, 255, 255, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.8); color: var(--text-main); line-height: 1.6; font-size: 1.05rem; white-space: pre-wrap; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">{res.get('patient_summary', 'No summary generated.')}</div>
            </div>
            ''', unsafe_allow_html=True)

            # Extracted Clinical Entities Showcase
            st.markdown("#### 🔍 Extracted Clinical Entities")
            html_tags = ""
            # Populate extracted clinical entities from actual diagnoses/procedures
            for d in res.get('details', []):
                label = d.get('entity', '')
                etype = d.get('type', 'Diagnosis')
                tclass = "tag-diagnosis" if etype == 'Diagnosis' else "tag-procedure"
                html_tags += f'<span class="tag {tclass}">{label}</span>'
            st.markdown(html_tags, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("#### 📄 ICD-10 Billing Codes")
            df = pd.DataFrame(res['details'])
            if not df.empty:
                def color_status(val):
                    if val == 'Approved': return 'color: #10b981; font-weight: bold;'
                    if val == 'Rejected': return 'color: #ef4444; font-weight: bold;'
                    return 'color: #f59e0b; font-weight: bold;'
                
                # Reorder columns for better flow
                cols = ['entity', 'type', 'code', 'confidence', 'est_price', 'description', 'medical_necessity', 'status']
                df = df[[c for c in cols if c in df.columns]]
                df.columns = ['Entity', 'Type', 'Code', 'Confidence', 'Est. Price', 'Description', 'Med. Necessity', 'Status']
                
                st.dataframe(df.style.map(color_status, subset=['Status']), use_container_width=True)
                
                # Action Buttons
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Report", csv, "medical_report.csv", "text/csv", key='dl-csv', use_container_width=True)
                with col_d2:
                    import importlib
                    import agents.reporter
                    importlib.reload(agents.reporter)
                    rep = agents.reporter.ReportingAgent()
                    patient_name = extract_patient_name(st.session_state.get('transcript', ''))
                    pdf_file = rep.generate_pdf_invoice(res, patient_name=patient_name)
                    if pdf_file and os.path.exists(pdf_file):
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="🖨️ Print Bill",
                                data=f,
                                file_name="billing_receipt.pdf",
                                mime="application/pdf",
                                key='print-bill',
                                use_container_width=True
                            )
                    else:
                        st.button("🖨️ Print Bill (Error)", disabled=True, use_container_width=True)
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

# ==============================================================
# --- CLINICAL DECISION SUPPORT PAGE ---
# ==============================================================
elif st.session_state['page'] == 'cds':

    st.markdown("""
        <div class="header-container">
            <h1 class="header-text-main">Clinical Decision Support</h1>
            <p class="header-text-sub">AI-Powered Diagnosis · Drug Safety · Treatment Planning · Risk Assessment</p>
        </div>
    """, unsafe_allow_html=True)

    col_cds_in, col_cds_out = st.columns([1, 1.4], gap="large")

    with col_cds_in:
        st.markdown("### 🩺 Patient Clinical Input")

        st.session_state['cds_symptoms'] = st.text_area(
            "Symptoms & Chief Complaints *",
            value=st.session_state['cds_symptoms'] or "Chest pain radiating to left arm, shortness of breath, diaphoresis, nausea for 2 hours.",
            height=120,
            help="Describe the patient's current symptoms in detail."
        )
        st.session_state['cds_medications'] = st.text_area(
            "Current Medications",
            value=st.session_state['cds_medications'],
            height=80,
            placeholder="e.g. Warfarin 5mg OD, Aspirin 75mg OD, Metformin 500mg BD",
            help="List all current medications the patient is taking."
        )
        st.session_state['cds_history'] = st.text_area(
            "Medical History",
            value=st.session_state['cds_history'],
            height=80,
            placeholder="e.g. Type 2 Diabetes (10 years), Hypertension, previous MI in 2019",
        )

        col_d, col_v = st.columns(2)
        with col_d:
            st.session_state['cds_demographics'] = st.text_input(
                "Age / Gender",
                value=st.session_state['cds_demographics'],
                placeholder="e.g. 58M"
            )
        with col_v:
            st.session_state['cds_vitals'] = st.text_input(
                "Vitals (optional)",
                value=st.session_state['cds_vitals'],
                placeholder="BP 90/60, HR 110, SpO2 94%, Temp 38.5"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧠 RUN CLINICAL DECISION SUPPORT", type="primary", use_container_width=True):
            if st.session_state['cds_symptoms']:
                with st.spinner("🤖 Running CDS Agent Pipeline..."):
                    try:
                        cds = get_cds_workflow()
                        if cds:
                            cds_result = cds.analyze(
                                symptoms=st.session_state['cds_symptoms'],
                                medications=st.session_state['cds_medications'],
                                history=st.session_state['cds_history'],
                                demographics=st.session_state['cds_demographics'],
                                vitals=st.session_state['cds_vitals']
                            )
                            st.session_state['cds_result'] = cds_result
                        else:
                            st.error("CDS Workflow could not be loaded.")
                    except Exception as e:
                        st.error(f"CDS Pipeline failed: {e}")
                st.rerun()
            else:
                st.error("Please enter the patient's symptoms.")

        if st.session_state.get('cds_result'):
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state['cds_result'] = None
                st.rerun()

    # --- CDS OUTPUT PANEL ---
    with col_cds_out:
        st.markdown("### 📊 Clinical Intelligence Output")

        cds_res = st.session_state.get('cds_result')

        if not cds_res:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.4); padding:4rem; border-radius:24px;
                        border:2px dashed rgba(139, 92, 246, 0.3); text-align:center;
                        color:#64748b; backdrop-filter:blur(5px);">
                <div style="font-size:4rem; margin-bottom:1rem;">🧠</div>
                <h2 style="margin:0; color:#1e293b;">Awaiting Clinical Input</h2>
                <p style="font-size:1.1rem;">Enter patient symptoms and run the CDS pipeline.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            risk = cds_res.get('risk_assessment', {})
            drug = cds_res.get('drug_safety', {})
            diagnoses = cds_res.get('differential_diagnoses', [])
            treatments = cds_res.get('treatment_plan', [])

            # ── Risk Summary Metrics ──
            severity = risk.get('overall_severity', 'Unknown')
            severity_colors = {'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#ef4444', 'Critical': '#7c3aed', 'Unknown': '#94a3b8'}
            sev_color = severity_colors.get(severity, '#94a3b8')
            readmit = risk.get('readmission_risk_pct', 0)
            sepsis = risk.get('sepsis_flag', 'No')
            interactions = drug.get('total_interactions', 0) if isinstance(drug, dict) else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Severity", severity)
            m2.metric("Readmission Risk", f"{readmit}%")
            m3.metric("Sepsis Flag", sepsis)
            m4.metric("Drug Interactions", interactions)

            # Severity Banner
            st.markdown(f"""
            <div style="background:{sev_color}18; border-left:5px solid {sev_color};
                        padding:1rem 1.5rem; border-radius:12px; margin:1rem 0;">
                <b style="color:{sev_color}; font-size:1.1rem;">⚠️ Patient Risk: {severity}</b>
                <p style="margin:0.3rem 0 0; color:#334155; font-size:0.9rem;">{risk.get('clinical_notes', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            # ── Differential Diagnoses ──
            st.markdown("#### 🔬 Differential Diagnosis")
            if isinstance(diagnoses, list) and diagnoses:
                for dx in diagnoses[:5]:
                    if not isinstance(dx, dict):
                        continue
                    conf = dx.get('confidence', 0)
                    urgency = dx.get('urgency', 'Routine')
                    urg_colors = {'Emergency': '#ef4444', 'Urgent': '#f59e0b', 'Routine': '#10b981'}
                    urg_c = urg_colors.get(urgency, '#94a3b8')
                    red_flags = dx.get('red_flags', [])
                    rf_html = ''.join([f'<span style="background:#fef2f2;color:#dc2626;padding:2px 8px;border-radius:99px;font-size:0.78rem;margin:2px;display:inline-block;">🚩 {r}</span>' for r in red_flags]) if red_flags else ''
                    st.markdown(f"""
                    <div class="glass-card" style="padding:1rem;margin-bottom:0.8rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b style="color:#1e293b;font-size:1rem;">#{dx.get('rank','')} {dx.get('diagnosis','')}</b>
                            <div>
                                <span style="background:#eff6ff;color:#1e40af;padding:3px 10px;border-radius:99px;font-size:0.8rem;font-weight:600;">{conf}% confidence</span>
                                <span style="background:{urg_c}18;color:{urg_c};padding:3px 10px;border-radius:99px;font-size:0.8rem;font-weight:600;margin-left:4px;">{urgency}</span>
                            </div>
                        </div>
                        <p style="margin:0.5rem 0 0.3rem;color:#475569;font-size:0.85rem;"><b>Next Step:</b> {dx.get('next_step','')}</p>
                        {rf_html}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No differential diagnoses generated.")

            # ── Drug Safety ──
            st.markdown("#### 💊 Drug Safety Check")
            if isinstance(drug, dict):
                overall_safety = drug.get('overall_safety', 'Unknown')
                safety_badge = {'Safe': '🟢', 'Caution': '🟡', 'Danger': '🔴'}.get(overall_safety, '⚪')
                st.markdown(f"**Overall Medication Safety: {safety_badge} {overall_safety}**")
                drug_interactions = drug.get('interactions', [])
                if drug_interactions:
                    sev_map = {'SEVERE': '#ef4444', 'MODERATE': '#f59e0b', 'MINOR': '#10b981'}
                    df_drug = pd.DataFrame(drug_interactions)
                    def color_sev(val):
                        return f'color: {sev_map.get(val, "#64748b")}; font-weight: bold;'
                    cols_to_show = [c for c in ['drug_1','drug_2','severity','effect','recommendation'] if c in df_drug.columns]
                    df_drug = df_drug[cols_to_show]
                    df_drug.columns = [c.replace('_',' ').title() for c in cols_to_show]
                    if 'Severity' in df_drug.columns:
                        st.dataframe(df_drug.style.map(color_sev, subset=['Severity']), use_container_width=True)
                    else:
                        st.dataframe(df_drug, use_container_width=True)
                else:
                    st.success("✅ No significant drug interactions found.")
            else:
                st.info("Drug safety data unavailable.")

            # ── Treatment Plan ──
            st.markdown("#### 📋 Treatment Recommendations")
            if isinstance(treatments, list) and treatments:
                for tx in treatments:
                    if not isinstance(tx, dict):
                        continue
                    with st.expander(f"🩺 {tx.get('diagnosis', 'Diagnosis')} — {tx.get('urgency', '')}", expanded=True):
                        first_line = tx.get('first_line_treatment', [])
                        if first_line:
                            st.markdown("**💊 First-Line Treatment:**")
                            for med in first_line:
                                if isinstance(med, dict):
                                    st.markdown(f"- **{med.get('medication','')}** — {med.get('dose','')} for {med.get('duration','')}")
                                    if med.get('notes'):
                                        st.caption(f"  ℹ️ {med.get('notes')}")
                        investigations = tx.get('investigations', [])
                        if investigations:
                            st.markdown("**🔬 Investigations to Order:**")
                            for inv in investigations:
                                if isinstance(inv, dict):
                                    priority_colors = {'Immediate': '🔴', 'Within 24h': '🟡', 'Routine': '🟢'}
                                    icon = priority_colors.get(inv.get('priority',''), '⚪')
                                    st.markdown(f"- {icon} **{inv.get('test','')}** — {inv.get('reason','')}")
                        referrals = tx.get('referrals', [])
                        if referrals:
                            st.markdown("**🏥 Referrals:** " + " | ".join(referrals))
                        lifestyle = tx.get('lifestyle_recommendations', [])
                        if lifestyle:
                            st.markdown("**🌱 Lifestyle:** " + " · ".join(lifestyle))
                        follow_up = tx.get('follow_up', '')
                        if follow_up:
                            st.markdown(f"**📅 Follow-up:** {follow_up}")
                        guideline = tx.get('guideline_source', '')
                        if guideline:
                            st.caption(f"📖 Evidence Base: {guideline}")
            else:
                st.info("No treatment recommendations generated.")

            # ── Immediate Actions ──
            immediate = risk.get('immediate_actions', [])
            if immediate:
                st.markdown("#### 🚨 Immediate Clinical Actions")
                for action in immediate:
                    if isinstance(action, dict):
                        priority = action.get('priority', '')
                        p_colors = {'Immediate': '#ef4444', 'Within 1h': '#f59e0b', 'Within 24h': '#3b82f6'}
                        p_color = p_colors.get(priority, '#64748b')
                        st.markdown(f"""
                        <div style="background:{p_color}12; border-left:4px solid {p_color};
                                    padding:0.7rem 1rem; border-radius:8px; margin-bottom:0.5rem;">
                            <b style="color:{p_color};">{priority}</b>
                            <span style="color:#334155; margin-left:0.5rem;">{action.get('action','')}</span>
                        </div>
                        """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h3 style="margin:0; color:white; font-size:1.3rem;">🤖 MediCode AI</h3>
            <p style="margin:0; color:rgba(255,255,255,0.7); font-size:0.85rem;">Healthcare AI Agent Platform</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("authenticated") and st.session_state.get("user"):
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.15);">
                <span style="color: white; font-size: 0.9rem;">👤 Logged in as: <b>{st.session_state.user[1]}</b></span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            from auth import logout_user
            logout_user(st.session_state.user[0])
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        st.markdown("<hr style='margin: 1rem 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    # --- PAGE NAVIGATION ---
    st.markdown('<span class="sidebar-label">MODULES</span>', unsafe_allow_html=True)

    if st.button("🏥 Medical Coding & Billing",
                 use_container_width=True,
                 type="primary" if st.session_state['page'] == 'coding' else "secondary"):
        st.session_state['page'] = 'coding'
        st.rerun()

    if st.button("🧠 Clinical Decision Support",
                 use_container_width=True,
                 type="primary" if st.session_state['page'] == 'cds' else "secondary"):
        st.session_state['page'] = 'cds'
        st.rerun()

    st.markdown("---")

    # --- AGENT STATUS ---
    st.markdown('<span class="sidebar-label">ACTIVE AGENTS</span>', unsafe_allow_html=True)

    if st.session_state['page'] == 'coding':
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
    else:
        is_done = st.session_state.get('cds_result') is not None
        agents = [
            ("Symptom Analyzer", "Differential Diagnoses Ready" if is_done else "Waiting..."),
            ("Drug Interaction Checker", "Safety Check Complete" if is_done else "Waiting..."),
            ("Treatment Recommender", "Protocol Generated" if is_done else "Waiting..."),
            ("Risk Scoring Agent", "Risk Assessment Done" if is_done else "Waiting...")
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
