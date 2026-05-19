#PATIENT CASE MODEL

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database.db import Base

class PatientCase(Base):

    __tablename__ = "patient_cases"

    id = Column(Integer, primary_key=True, index=True)

    transcript = Column(Text)

    total_diagnoses = Column(Integer)

    total_codes = Column(Integer)

    confidence_score = Column(Float)

    total_bill = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    icd_codes = relationship("ICDCode", back_populates="patient_case")

    entities = relationship("ClinicalEntity", back_populates="patient_case")

#ICD CODE MODEL


class ICDCode(Base):

    __tablename__ = "icd_codes"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(Integer, ForeignKey("patient_cases.id"))

    diagnosis = Column(String)

    icd_code = Column(String)

    status = Column(String)

    patient_case = relationship("PatientCase", back_populates="icd_codes")

#ENTITY MODEL

class ClinicalEntity(Base):

    __tablename__ = "clinical_entities"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(Integer, ForeignKey("patient_cases.id"))

    entity_text = Column(String)

    entity_type = Column(String)

    patient_case = relationship("PatientCase", back_populates="entities")