import pandas as pd
import json

class ReportingAgent:
    def __init__(self):
        pass

    def generate_report(self, extracted_info, codes, audit_results):
        # Combine all data into a clean structure
        report = {
            "summary": {
                "total_diagnoses": len(extracted_info.get("diagnoses", [])),
                "total_codes": len(codes)
            },
            "details": []
        }

        # Map audit results to codes for the final report
        audit_map = {a['icd10_code']: a for a in audit_results if 'icd10_code' in a}

        for item in codes:
            code = item.get('icd10_code')
            audit = audit_map.get(code, {"status": "Not Audited", "confidence_score": 0, "reason": "No audit data"})
            
            report["details"].append({
                "diagnosis": item.get('diagnosis'),
                "icd10_code": code,
                "description": item.get('description'),
                "status": audit.get('status'),
                "confidence": audit.get('confidence_score'),
                "reason": audit.get('reason')
            })

        return report

    def save_to_excel(self, report, filename="medical_billing_report.xlsx"):
        df = pd.DataFrame(report["details"])
        df.to_excel(filename, index=False)
        return filename
