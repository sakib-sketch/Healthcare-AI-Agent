from database.models import PatientCase, ICDCode, ClinicalEntity

def save_case(db, transcript, result):

    patient_case = PatientCase(

        transcript=transcript,

        total_diagnoses=result['summary']['total_diagnoses'],

        total_codes=result['summary']['total_codes'],

        confidence_score=94.0
    )

    db.add(patient_case)

    db.commit()

    db.refresh(patient_case)

    # Save ICD codes
    for row in result['details']:

        icd = ICDCode(

            case_id=patient_case.id,

            diagnosis=row['diagnosis'],

            icd_code=row['icd10_code'],

            status=row['status']
        )

        db.add(icd)

    db.commit()

    return patient_case.id