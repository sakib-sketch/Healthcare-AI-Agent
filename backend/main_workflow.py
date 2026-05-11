from agents import ExtractorAgent, CoderAgent, AuditorAgent, ReportingAgent

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
