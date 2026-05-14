import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from database.db import SessionLocal
from database.models import PatientCase, ICDCode

db = SessionLocal()
cases = db.query(PatientCase).order_by(PatientCase.id.desc()).limit(5).all()

print(f"Total Cases in DB: {db.query(PatientCase).count()}")
print(f"Total ICD Codes in DB: {db.query(ICDCode).count()}")

for case in cases:
    print(f"\nCase ID: {case.id} | Transcript: {case.transcript[:50]}...")
    codes = db.query(ICDCode).filter(ICDCode.case_id == case.id).all()
    print(f"  ICD Codes ({len(codes)}):")
    for code in codes:
        print(f"    - {code.icd_code} ({code.diagnosis}) | Status: {code.status}")

db.close()
