import os
print(f"LOADING WORKFLOW FROM: {os.path.abspath(__file__)}")

from agents import ExtractorAgent, CoderAgent, AuditorAgent, ReportingAgent, HumanizerAgent
from database.db import SessionLocal
from database.crud import save_case

class MedicalCodingWorkflow:
    def __init__(self):
        self.extractor = ExtractorAgent()
        self.coder = CoderAgent()
        self.auditor = AuditorAgent()
        self.reporter = ReportingAgent()
        self.humanizer = HumanizerAgent()

    def process_note(self, clinical_note):
        print("Step 1: Extracting medical entities...")
        extracted_info = self.extractor.extract(clinical_note)
        
        print("Step 2: Mapping to ICD-10 and CPT codes...")
        diagnoses = extracted_info.get("diagnoses", []) or extracted_info.get("diagnosis", [])
        procedures = extracted_info.get("procedures", [])
        codes = self.coder.map_codes(diagnoses, procedures)
        
        print("Step 3: Auditing results...")
        audit_results = self.auditor.audit(clinical_note, codes)
        
        print("Step 4: Generating final report...")
        final_report = self.reporter.generate_report(extracted_info, codes, audit_results)

        print("Step 5: Generating patient-friendly summary...")
        final_report['patient_summary'] = self.humanizer.generate_summary(clinical_note)
        
        # SAVE TO DATABASE
        print("Step 6: Saving results to database...")
        db = SessionLocal()
        try:
            case_id = save_case(db, clinical_note, final_report)
            print(f"Case saved to database with ID: {case_id}")
            final_report['case_id'] = case_id
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            db.close()
            
        print(f"DEBUG: final_report keys: {final_report.keys()}")
        return final_report
