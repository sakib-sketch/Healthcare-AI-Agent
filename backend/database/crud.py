from database.models import PatientCase, ICDCode, ClinicalEntity
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

            diagnosis=row.get('entity') or row.get('diagnosis'),

            icd_code=row.get('code') or row.get('icd10_code'),

            status=row.get('status')
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