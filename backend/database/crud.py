from database.models import PatientCase, ICDCode, ClinicalEntity, ClinicalDecisionRecord
from database.db import Base, engine

# Ensure database tables are created automatically
Base.metadata.create_all(bind=engine)

def save_case(db, transcript, result):

    # Calculate real average confidence from the model's output
    details = result.get('details', [])
    avg_conf = 0.0
    if details:
        confidences = [float(d.get('confidence', 0)) for d in details if d.get('confidence') is not None]
        if confidences:
            avg = sum(confidences) / len(confidences)
            avg_conf = (avg * 100) if avg <= 1.0 else avg

    patient_case = PatientCase(

        transcript=transcript,

        total_diagnoses=result['summary']['total_diagnoses'],

        total_codes=result['summary']['total_codes'],

        confidence_score=avg_conf,
        
        total_bill=result['summary'].get('total_revenue', 0.0)
    )

    db.add(patient_case)

    db.commit()

    db.refresh(patient_case)

    # Save ICD codes
    for row in result['details']:

        icd = ICDCode(

            case_id=patient_case.id,

            diagnosis=row.get('entity') or row.get('diagnosis') or '',

            icd_code=row.get('code') or row.get('icd10_code') or '',

            status=row.get('status') or 'Pending'
        )

        db.add(icd)

        # Save Clinical Entity
        entity = ClinicalEntity(
            case_id=patient_case.id,
            entity_text=row.get('entity') or row.get('diagnosis'),
            entity_type=row.get('type', 'Diagnosis')
        )
        db.add(entity)

    db.commit()

    return patient_case.id


def save_cds_result(db, symptom_input, report):
    """Persists a Clinical Decision Support pipeline result to the database."""

    risk = report.get("risk_assessment", {})
    drug = report.get("drug_safety", {})
    diagnoses = report.get("differential_diagnoses", [])
    inp = report.get("input_summary", {})

    # Extract top diagnosis safely
    top_dx = ""
    top_conf = 0.0
    if isinstance(diagnoses, list) and diagnoses:
        first = diagnoses[0]
        if isinstance(first, dict):
            top_dx = first.get("diagnosis", "")
            top_conf = float(first.get("confidence", 0))

    record = ClinicalDecisionRecord(
        symptom_input=symptom_input,
        demographics=inp.get("demographics", ""),
        medications_input=inp.get("medications", ""),
        history_input=inp.get("history", ""),
        overall_severity=risk.get("overall_severity", "Unknown"),
        readmission_risk_pct=float(risk.get("readmission_risk_pct", 0)),
        sepsis_flag=risk.get("sepsis_flag", "No"),
        drug_safety_status=drug.get("overall_safety", "Unknown") if isinstance(drug, dict) else "Unknown",
        total_interactions=int(drug.get("total_interactions", 0)) if isinstance(drug, dict) else 0,
        top_diagnosis=top_dx,
        top_diagnosis_confidence=top_conf
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record.id