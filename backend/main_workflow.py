from agents import ExtractorAgent, CoderAgent, AuditorAgent, ReportingAgent
from database.db import SessionLocal
from database.crud import save_case

class MedicalCodingWorkflow:
    def __init__(self):
        self.extractor = ExtractorAgent()
        self.coder = CoderAgent()
        self.auditor = AuditorAgent()
        self.reporter = ReportingAgent()

    def process_note(self, clinical_note):
        print("Step 1: Extracting medical entities...")
        extracted_info = self.extractor.extract(clinical_note)
        
        print("Step 2: Mapping to ICD-10 codes...")
        diagnoses = extracted_info.get("diagnoses", [])
        codes = self.coder.map_codes(diagnoses)
        
        print("Step 3: Auditing results...")
        audit_results = self.auditor.audit(clinical_note, codes)
        
        print("Step 4: Generating final report...")
        final_report = self.reporter.generate_report(extracted_info, codes, audit_results)
        
        # SAVE TO DATABASE
        print("Step 5: Saving results to database...")
        db = SessionLocal()
        try:
            case_id = save_case(db, clinical_note, final_report)
            print(f"Case saved to database with ID: {case_id}")
            final_report['case_id'] = case_id
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            db.close()
            
        return final_report

if __name__ == "__main__":
    # Test Note
    sample_note = """
    Patient is a 45-year-old male complaining of persistent cough and shortness of breath for 2 weeks. 
    Physical exam reveals wheezing in both lungs. 
    Diagnosis: Acute Bronchitis and suspected Hypertension.
    Prescribed Albuterol inhaler and Lisinopril.
    """
    
    workflow = MedicalCodingWorkflow()
    report = workflow.process_note(sample_note)
    
    import json
    print(json.dumps(report, indent=4))
