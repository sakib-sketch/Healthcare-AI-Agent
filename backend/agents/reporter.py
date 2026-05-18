import pandas as pd
import json

class ReportingAgent:
    def __init__(self):
        # 💰 Mocked Pricing Table for Billing (Standard CPT rates)
        self.price_list = {
            "99203": 150.00, # New Patient Office Visit
            "99213": 75.00,  # Established Patient Visit
            "99214": 110.00, # Complex Patient Visit
            "80053": 45.00,  # Blood Test (CMP)
            "71045": 60.00,  # Chest X-Ray
            "93000": 35.00,  # EKG
            "DEFAULT_PROCEDURE": 100.00
        }

    def generate_report(self, extracted_info, codes, audit_results):
        # Combine all data into a clean structure
        report = {
            "summary": {
                "total_diagnoses": len(extracted_info.get("diagnoses", [])),
                "total_procedures": len(extracted_info.get("procedures", [])),
                "total_codes": len(codes),
                "total_revenue": 0.0
            },
            "details": []
        }

        # Map audit results to codes for the final report
        audit_map = {a['code']: a for a in audit_results if 'code' in a}

        total_rev = 0
        for item in codes:
            code = item.get('code')
            audit = audit_map.get(code, {"status": "Not Audited", "confidence_score": 0, "reason": "No audit data"})
            
            # Calculate price if it's a procedure
            est_price = 0
            if item.get('type') == 'Procedure':
                est_price = self.price_list.get(code, self.price_list['DEFAULT_PROCEDURE'])
                total_rev += est_price

            report["details"].append({
                "entity": item.get('entity'),
                "type": item.get('type'),
                "code": code,
                "description": item.get('description'),
                "status": audit.get('status'),
                "confidence": audit.get('confidence_score'),
                "medical_necessity": audit.get('medical_necessity', 'N/A'),
                "est_price": est_price,
                "reason": audit.get('reason')
            })

        report["summary"]["total_revenue"] = total_rev
        return report

    def save_to_excel(self, report, filename="medical_billing_report.xlsx"):
        df = pd.DataFrame(report["details"])
        df.to_excel(filename, index=False)
        return filename

    def generate_pdf_invoice(self, report, patient_name="John Doe", filename="invoice.pdf"):
        try:
            from fpdf import FPDF
        except ImportError:
            return None

        pdf = FPDF()
        pdf.add_page()

        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "MediCode AI - Automated Hospital Billing", ln=True, align="C")
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Patient Invoice", ln=True, align="C")
        pdf.ln(10)

        # Patient Info
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, "Patient Name:")
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, patient_name, ln=True)
        pdf.ln(10)

        # Billing Details Table
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 10, "Type", border=1)
        pdf.cell(30, 10, "Code", border=1)
        pdf.cell(100, 10, "Description", border=1)
        pdf.cell(30, 10, "Price", border=1, ln=True)

        pdf.set_font("Arial", '', 10)
        for item in report["details"]:
            pdf.cell(30, 10, str(item['type']), border=1)
            pdf.cell(30, 10, str(item['code']), border=1)
            # Truncate description to fit
            desc = str(item['description'])[:50]
            pdf.cell(100, 10, desc, border=1)
            price_str = f"${item['est_price']:.2f}" if item['type'] == 'Procedure' else "-"
            pdf.cell(30, 10, price_str, border=1, ln=True)

        pdf.ln(10)

        # Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(160, 10, "Total Estimated Revenue:", align="R")
        pdf.cell(30, 10, f"${report['summary']['total_revenue']:.2f}", ln=True)

        pdf.output(filename)
        return filename
