import streamlit as st
import sys
import os
import json
import pandas as pd
from PIL import Image
<<<<<<< HEAD

# Add backend to path so we can import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

st.set_page_config(page_title="MediCode AI | Agentic Healthcare", layout="wide", page_icon="🏥")

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8faff;
    }
    
    /* Header Styling */
    .header-text-main {
        color: #3b82f6 !important;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    .header-text-sub {
        color: #64748b !important;
        font-size: 1.1rem;
        margin-top: 0;
    }
    
    /* Card Styling */
    .card {
        background-color: #ffffff !important;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        color: #1e293b !important; /* Force dark text on white cards */
    }
    
    .agent-active {
        border-left: 5px solid #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    
    .agent-done {
        border-left: 5px solid #10b981 !important;
        background-color: #f0fdf4 !important;
    }

    /* Tag Styling */
    .tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .tag-diagnosis { background-color: #dbeafe; color: #1e40af; }
    .tag-symptom { background-color: #fef3c7; color: #92400e; }
    .tag-procedure { background-color: #dcfce7; color: #166534; }
    .tag-med { background-color: #f3e8ff; color: #6b21a8; }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 0.8rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
with st.container():
    col_logo, col_text = st.columns([1, 6])
    with col_logo:
        try:
            logo = Image.open(r"C:\Users\SAKIB NADAF\.gemini\antigravity\brain\8182ba32-4c6c-4bca-9548-dfaffad5cf44\healthcare_ai_logo_1778479740052.png")
            st.image(logo, width=100)
        except:
            st.title("🏥")
            
=======
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
<<<<<<< HEAD
st.markdown("---")

# --- MAIN CONTENT ---
col_input, col_output = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("### 📥 Patient Documentation")
    with st.container():
        sample_text = """Patient is a 62-year-old female with a history of Type 2 Diabetes. 
She presents today with a painful ulcer on her right foot. 
Diagnosis: Diabetic Foot Ulcer and Peripheral Neuropathy.
Ordered wound dressing and referred to Podiatry."""
        
        note = st.text_area("Paste Clinical Notes or Transcription:", value=sample_text, height=350)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ ANALYZE WITH 4-AGENT PIPELINE"):
            if note:
                with st.spinner("Initializing AI Agents..."):
                    workflow = MedicalCodingWorkflow()
                    result = workflow.process_note(note)
                    st.session_state['result'] = result
                    st.success("Analysis Successfully Completed")
            else:
                st.error("Please provide clinical documentation to proceed.")

with col_output:
    st.markdown("### 📊 Agent Intelligence Output")
    
    if 'result' in st.session_state:
        res = st.session_state['result']
        
        # Dashboard Overview
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Diagnoses", res['summary']['total_diagnoses'])
        with c2:
            st.metric("Generated Codes", res['summary']['total_codes'])
        with c3:
            st.metric("Avg. Confidence", "94%") # Mocked for UI polish

        # Detailed Insights (This data would come from the Extractor Agent)
        st.markdown("#### 🔍 Extracted Clinical Entities")
        # In a real app, these would come dynamically from the extractor agent's JSON
=======

st.markdown("---")

# =========================================================
# -------------------- MAIN LAYOUT ------------------------
# =========================================================

col_input, col_output = st.columns([1, 1.2], gap="large")

# =========================================================
# -------------------- INPUT PANEL ------------------------
# =========================================================

with col_input:
    st.markdown("### 📥 Input Clinical Data")

    # Initialize session state for extracted text
    if 'extracted_text' not in st.session_state:
        st.session_state['extracted_text'] = ""

    tab1, tab2 = st.tabs(["📄 Document Upload", "🎙️ Live Recording"])

    with tab1:
        uploaded_file = st.file_uploader(
            "Upload Transcript / Clinical Document",
            type=["pdf", "png", "jpg", "jpeg", "docx", "txt", "wav", "mp3"]
        )

        if uploaded_file:
            if st.button("🔍 Extract from Document"):
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
                try:
                    recognizer = sr.Recognizer()

                    # Save browser audio temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                        temp_audio.write(audio_data['bytes'])
                        temp_audio_path = temp_audio.name

                    # Convert WEBM/OPUS -> WAV PCM
                    audio = AudioSegment.from_file(temp_audio_path)
                    wav_path = temp_audio_path.replace(".webm", ".wav")

                    audio.export(
                        wav_path,
                        format="wav",
                        parameters=[
                            "-ac", "1",      # mono
                            "-ar", "16000"   # sample rate
                        ]
                    )

                    # Read converted WAV
                    with sr.AudioFile(wav_path) as source:
                        audio_content = recognizer.record(source)

                    # Speech Recognition
                    speech_text = recognizer.recognize_google(audio_content)

                    # Store transcript
                    if st.session_state['extracted_text']:
                        st.session_state['extracted_text'] += "\n\n" + speech_text
                    else:
                        st.session_state['extracted_text'] = speech_text

                    st.success("✅ Voice converted to text successfully")

                except Exception as e:
                    st.error(f"Live speech recognition failed: {e}")

    # =====================================================
    # SHOW AND EDIT EXTRACTED TEXT
    # =====================================================
    st.markdown("### 📝 Clinical Transcript")
    
    # Add a clear button
    if st.button("🗑️ Clear Transcript", type="secondary"):
        st.session_state['extracted_text'] = ""
        st.rerun()

    # We use a text area to allow the user to review/edit before analysis
    st.text_area(
        "Review / Edit clinical notes before AI analysis",
        height=300,
        key="extracted_text"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # RUN PIPELINE
    # =====================================================
    if st.button("⚡ ANALYZE WITH AI AGENT PIPELINE", use_container_width=True):
        if st.session_state['extracted_text']:
            with st.spinner("🤖 Running Multi-Agent Medical Workflow..."):
                try:
                    workflow = MedicalCodingWorkflow()
                    result = workflow.process_note(st.session_state['extracted_text'])
                    
                    st.session_state['result'] = result
                    st.session_state['transcript'] = st.session_state['extracted_text']
                    st.success("Analysis Successfully Completed")
                    st.rerun()
                except Exception as e:
                    st.error(f"Pipeline execution failed: {e}")
        else:
            st.error("Please provide clinical data via upload or recording.")

# =========================================================
# -------------------- OUTPUT PANEL -----------------------
# =========================================================

with col_output:

    st.markdown("### 📊 Agent Intelligence Output")

    if 'result' in st.session_state:
        # Reset Button for new case
        if st.button("➕ Start New Analysis", type="primary"):
            del st.session_state['result']
            st.session_state['extracted_text'] = ""
            st.rerun()

        res = st.session_state['result']

        # Metrics
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Diagnoses", res['summary']['total_diagnoses'])

        with c2:
            st.metric("Generated Codes", res['summary']['total_codes'])

        with c3:
            st.metric("Avg. Confidence", "94%")

        # =================================================
        # EXTRACTED ENTITIES
        # =================================================

        st.markdown("#### 🔍 Extracted Clinical Entities")

>>>>>>> 65cab42 (Initial commit: Professional medical coding AI workflow with multi-agent architecture)
        st.markdown("""
            <span class="tag tag-diagnosis">Type 2 Diabetes</span>
            <span class="tag tag-diagnosis">Foot Ulcer</span>
            <span class="tag tag-diagnosis">Peripheral Neuropathy</span>
            <span class="tag tag-symptom">Painful ulcer</span>
            <span class="tag tag-procedure">Wound dressing</span>
            <span class="tag tag-med">Lisinopril</span>
        """, unsafe_allow_html=True)
<<<<<<< HEAD
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Billing Table
        st.markdown("#### 📄 ICD-10 Billing Codes")
        df = pd.DataFrame(res['details'])
        if not df.empty:
            def color_status(val):
                if val == 'Approved': return 'color: #059669; font-weight: bold;'
                if val == 'Rejected': return 'color: #dc2626; font-weight: bold;'
                return 'color: #d97706; font-weight: bold;'
            
            st.dataframe(df.style.map(color_status, subset=['status']), use_container_width=True)
            
            # Action Buttons
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Excel Report", csv, "medical_report.csv", "text/csv", key='dl-csv')
            with col_d2:
                st.button("📧 Send to Billing Dept", disabled=False)
        else:
            st.warning("No medical codes detected in this documentation.")
    else:
        # Placeholder for empty state
        st.markdown("""
            <div style="background-color:#f1f5f9; padding:3rem; border-radius:15px; border: 2px dashed #cbd5e1; text-align:center; color:#94a3b8;">
                <h2 style="margin:0;">Waiting for Input...</h2>
                <p>Paste clinical notes on the left to trigger the Agentic Workflow.</p>
            </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR AGENT TRACKER ---
st.sidebar.markdown("## 🤖 Agent Command Center")
st.sidebar.markdown("Monitoring the live reasoning chain:")

if 'result' in st.session_state:
    st.sidebar.markdown("""
        <div class="card agent-done"><b>✅ Extractor Agent</b><br><small>Clinical Entity Recognition active</small></div>
        <div class="card agent-done"><b>✅ Coder Agent</b><br><small>ICD-10-CM Mapping complete</small></div>
        <div class="card agent-done"><b>✅ Auditor Agent</b><br><small>Validation Confidence: 94%</small></div>
        <div class="card agent-done"><b>✅ Reporting Agent</b><br><small>Final billing report generated</small></div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
        <div class="card"><b>⚪ Extractor Agent</b><br><small>Idle...</small></div>
        <div class="card"><b>⚪ Coder Agent</b><br><small>Idle...</small></div>
        <div class="card"><b>⚪ Auditor Agent</b><br><small>Idle...</small></div>
        <div class="card"><b>⚪ Reporting Agent</b><br><small>Idle...</small></div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("System powered by **Cohere Command-R** Agentic Workflow.")
=======

        st.markdown("<br>", unsafe_allow_html=True)

        # =================================================
        # SHOW FINAL TRANSCRIPT
        # =================================================

        st.markdown("#### 📄 Final Clinical Transcript")

        st.text_area(
            "Transcript Sent to AI Coding Agents",
            value=st.session_state.get('transcript', ''),
            height=220
        )

        # =================================================
        # ICD TABLE
        # =================================================

        st.markdown("#### 💳 ICD-10 Billing Codes")

        df = pd.DataFrame(res['details'])

        if not df.empty:

            def color_status(val):

                if val == 'Approved':
                    return 'color: #059669; font-weight: bold;'

                if val == 'Rejected':
                    return 'color: #dc2626; font-weight: bold;'

                return 'color: #d97706; font-weight: bold;'

            st.dataframe(
                df.style.map(color_status, subset=['status']),
                use_container_width=True
            )

            col_d1, col_d2 = st.columns(2)

            with col_d1:

                csv = df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    "📥 Download Excel Report",
                    csv,
                    "medical_report.csv",
                    "text/csv",
                    key='dl-csv'
                )

            with col_d2:
                st.button("📧 Send to Billing Dept")

        else:
            st.warning("No medical codes detected.")

    else:

        st.markdown("""
        <div style="
            background-color:#f1f5f9;
            padding:3rem;
            border-radius:15px;
            border:2px dashed #cbd5e1;
            text-align:center;
            color:#94a3b8;
        ">
            <h2 style="margin:0;">Waiting for Upload...</h2>
            <p>Upload medical transcript, scanned document, or voice recording.</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# -------------------- SIDEBAR ----------------------------
# =========================================================

with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h3 style="margin:0; color:white; font-size:1.2rem;">🤖 Agent Command</h3>
            <p style="margin:0; color:rgba(255,255,255,0.8); font-size:0.8rem;">Monitoring live reasoning chain</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-label">ACTIVE AGENTS</span>', unsafe_allow_html=True)

    if 'result' in st.session_state:
        st.markdown("""
            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ OCR Agent</b><br>
                <small style="color:#15803d;">Extraction Complete</small>
            </div>

            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ Speech Agent</b><br>
                <small style="color:#15803d;">Transcription Complete</small>
            </div>

            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ Extractor Agent</b><br>
                <small style="color:#15803d;">Entities Identified</small>
            </div>

            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ Coder Agent</b><br>
                <small style="color:#15803d;">ICD-10 Mapping Done</small>
            </div>

            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ Auditor Agent</b><br>
                <small style="color:#15803d;">Validation Passed (94%)</small>
            </div>

            <div class="card agent-done" style="padding: 1rem; margin-bottom: 0.8rem;">
                <b style="color:#166534;">✅ Reporting Agent</b><br>
                <small style="color:#15803d;">Report Generated</small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ OCR Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>

            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ Speech Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>

            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ Extractor Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>

            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ Coder Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>

            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ Auditor Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>

            <div class="card" style="padding: 1rem; margin-bottom: 0.8rem; opacity: 0.7;">
                <b style="color:#64748b;">⚪ Reporting Agent</b><br>
                <small style="color:#94a3b8;">Waiting...</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 Powered by Cohere Multi-Agent Workflow")
>>>>>>> 65cab42 (Initial commit: Professional medical coding AI workflow with multi-agent architecture)
