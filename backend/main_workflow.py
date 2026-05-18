from agents import ExtractorAgent, CoderAgent, AuditorAgent, ReportingAgent, PrivacyAgent

class MedicalCodingWorkflow:
    def __init__(self):
        self.privacy = PrivacyAgent()
        self.extractor = ExtractorAgent()
        self.coder = CoderAgent()
        self.auditor = AuditorAgent()
        self.reporter = ReportingAgent()

    def process_note(self, clinical_note):
        print("Step 0: Anonymizing patient data (HIPAA Compliance)...")
        anonymized_note = self.privacy.anonymize(clinical_note)

        print("Step 1: Extracting medical entities...")
        extracted_info = self.extractor.extract(anonymized_note)
        
        print("Step 2: Mapping to ICD-10 and CPT codes...")
        diagnoses = extracted_info.get("diagnoses", [])
        procedures = extracted_info.get("procedures", [])
        codes = self.coder.map_codes(diagnoses, procedures)
        
        print("Step 3: Auditing results...")
        audit_results = self.auditor.audit(anonymized_note, codes)
        
        print("Step 4: Generating final report...")
        final_report = self.reporter.generate_report(extracted_info, codes, audit_results)
        
        # Attach the anonymized note to the report so UI can display it
        final_report["anonymized_note"] = anonymized_note
        return final_report
