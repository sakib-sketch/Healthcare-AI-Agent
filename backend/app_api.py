import sys
import os

# Ensure backend modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import bcrypt
import tempfile

# --- DB & Auth imports ---
from database.db import get_connection, create_users_table, SessionLocal
from database.crud import save_case
from database.models import PatientCase, ICDCode, ClinicalEntity
from email_validator import validate_email, EmailNotValidError

# --- Workflow import ---
from main_workflow import MedicalCodingWorkflow

# =========================================================
# App Setup
# =========================================================
app = FastAPI(title="MediCode AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure users table exists on startup
@app.on_event("startup")
def startup():
    create_users_table()

# =========================================================
# Pydantic Schemas
# =========================================================
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    user_id: int

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

class AnalyzeRequest(BaseModel):
    clinical_note: str

# =========================================================
# Auth Helpers
# =========================================================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# =========================================================
# Auth Routes
# =========================================================
@app.post("/api/auth/register")
def register(req: RegisterRequest):
    try:
        validate_email(req.email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(req.password)
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (req.name, req.email, hashed)
        )
        conn.commit()
        return {"success": True, "message": "Registration successful"}
    except Exception as e:
        conn.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/api/auth/login")
def login(req: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (req.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        stored_password = user[3]
        if not verify_password(req.password, stored_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Update login timestamp
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP, is_logged_in = TRUE WHERE id = %s",
            (user[0],)
        )
        conn.commit()

        return {
            "success": True,
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
            }
        }
    finally:
        conn.close()


@app.post("/api/auth/logout")
def logout(req: LogoutRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET last_logout = CURRENT_TIMESTAMP, is_logged_in = FALSE WHERE id = %s",
            (req.user_id,)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/api/auth/reset-password")
def reset_password(req: ResetPasswordRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(req.new_password)
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed, req.email))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"success": True, "message": "Password updated successfully"}
    finally:
        conn.close()


# =========================================================
# Document Processing Route
# =========================================================
@app.post("/api/process/document")
async def process_document(file: UploadFile = File(...)):
    """Extract text from uploaded PDF, DOCX, or TXT files."""
    filename = file.filename.lower()
    content = await file.read()

    try:
        if filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")

        elif filename.endswith(".pdf"):
            import pdf2image
            import pytesseract
            from PIL import Image
            import io
            images = pdf2image.convert_from_bytes(content)
            text = "\n".join(pytesseract.image_to_string(img) for img in images)

        elif filename.endswith(".docx"):
            import docx
            import io
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)

        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        return {"success": True, "text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing error: {str(e)}")


# =========================================================
# Audio Processing Route
# =========================================================
@app.post("/api/process/audio")
async def process_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio (webm/wav/mp3) using Google Speech-to-Text."""
    content = await file.read()
    suffix = "." + (file.filename.split(".")[-1] if "." in file.filename else "webm")

    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        import io

        audio_seg = AudioSegment.from_file(io.BytesIO(content))
        wav_io = io.BytesIO()
        audio_seg.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return {"success": True, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription error: {str(e)}")


# =========================================================
# Main Workflow Analysis Route
# =========================================================
_workflow = None

def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = MedicalCodingWorkflow()
    return _workflow


@app.post("/api/workflow/analyze")
def analyze(req: AnalyzeRequest):
    """Run the full MedicalCodingWorkflow on a clinical note."""
    if not req.clinical_note.strip():
        raise HTTPException(status_code=400, detail="Clinical note cannot be empty")

    try:
        workflow = get_workflow()
        result = workflow.process_note(req.clinical_note)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


# =========================================================
# Reports Route
# =========================================================
@app.get("/api/reports/bill/{case_id}")
def download_bill(case_id: int):
    """Download the invoice PDF for a given case ID."""
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "invoice.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"invoice_{case_id}.pdf")


# =========================================================
# Health Check
# =========================================================
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "MediCode AI API"}
