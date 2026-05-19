import re

class HumanizerAgent:
    """
    Converts complex clinical notes into simple human-readable summaries.
    """

    def __init__(self):
        self.medical_dictionary = {

            # =========================
            # CARDIOLOGY
            # =========================
            "hypertension": "high blood pressure",
    "hypotension": "low blood pressure",
    "myocardial infarction": "heart attack",
    "cardiac arrest": "heart stopped beating",
    "arrhythmia": "irregular heartbeat",
    "tachycardia": "fast heart rate",
    "bradycardia": "slow heart rate",
    "angina": "chest pain caused by reduced blood flow to the heart",
    "atherosclerosis": "hardening of the arteries",
    "congestive heart failure": "heart weakness causing fluid buildup",
    "coronary artery disease": "blocked heart arteries",
    "cardiomegaly": "enlarged heart",
    "murmur": "abnormal heart sound",

    # =========================
    # RESPIRATORY
    # =========================
    "dyspnea": "difficulty breathing",
    "hypoxia": "low oxygen levels",
    "pneumonia": "lung infection",
    "asthma": "airway breathing condition",
    "copd": "chronic lung disease affecting breathing",
    "pulmonary embolism": "blood clot in the lungs",
    "bronchitis": "inflammation of the airways",
    "pleural effusion": "fluid around the lungs",
    "respiratory failure": "lungs unable to provide enough oxygen",
    "pulmonary edema": "fluid buildup in the lungs",

    # =========================
    # NEUROLOGY
    # =========================
    "neuropathy": "nerve damage",
    "stroke": "brain blood flow blockage or bleeding",
    "cerebrovascular accident": "stroke",
    "seizure": "sudden abnormal brain activity",
    "epilepsy": "condition causing repeated seizures",
    "syncope": "fainting",
    "migraine": "severe headache",
    "dementia": "memory and thinking decline",
    "parkinsonism": "movement disorder symptoms",
    "multiple sclerosis": "disease affecting nerves",

    # =========================
    # GASTROENTEROLOGY
    # =========================
    "gastritis": "stomach inflammation",
    "hepatitis": "liver inflammation",
    "cirrhosis": "scarring of the liver",
    "constipation": "difficulty passing stool",
    "diarrhea": "frequent loose stool",
    "gastroesophageal reflux disease": "acid reflux",
    "gerd": "acid reflux",
    "peptic ulcer": "sore in the stomach lining",
    "colitis": "colon inflammation",
    "appendicitis": "inflamed appendix",

    # =========================
    # ENDOCRINOLOGY
    # =========================
    "diabetes mellitus": "diabetes",
    "hyperglycemia": "high blood sugar",
    "hypoglycemia": "low blood sugar",
    "hypothyroidism": "underactive thyroid",
    "hyperthyroidism": "overactive thyroid",
    "obesity": "excess body weight",
    "metabolic syndrome": "group of conditions increasing disease risk",

    # =========================
    # RENAL / UROLOGY
    # =========================
    "renal failure": "kidney failure",
    "acute kidney injury": "sudden kidney damage",
    "chronic kidney disease": "long-term kidney damage",
    "nephrolithiasis": "kidney stones",
    "urinary tract infection": "urine infection",
    "hematuria": "blood in urine",
    "proteinuria": "protein in urine",

    # =========================
    # MUSCULOSKELETAL
    # =========================
    "fracture": "broken bone",
    "arthritis": "joint inflammation",
    "osteoporosis": "weak bones",
    "scoliosis": "curved spine",
    "sprain": "ligament injury",
    "strain": "muscle injury",
    "tendonitis": "tendon inflammation",
    "osteomyelitis": "bone infection",

    # =========================
    # ONCOLOGY
    # =========================
    "carcinoma": "cancer",
    "malignant": "cancerous",
    "benign": "non-cancerous",
    "metastasis": "spread of cancer",
    "tumor": "abnormal growth",
    "neoplasm": "abnormal tissue growth",
    "lymphoma": "cancer of the lymph system",
    "leukemia": "blood cancer",

    # =========================
    # INFECTIOUS DISEASES
    # =========================
    "sepsis": "serious body-wide infection",
    "cellulitis": "skin infection",
    "abscess": "collection of pus",
    "viral infection": "infection caused by a virus",
    "bacterial infection": "infection caused by bacteria",
    "fungal infection": "infection caused by fungus",
    "covid-19": "coronavirus infection",
    "influenza": "flu infection",

    # =========================
    # GENERAL CLINICAL TERMS
    # =========================
    "edema": "swelling",
    "fatigue": "extreme tiredness",
    "fever": "high body temperature",
    "nausea": "feeling like vomiting",
    "vomiting": "throwing up",
    "anemia": "low red blood cell count",
    "cyanosis": "bluish skin due to low oxygen",
    "dehydration": "lack of body fluids",
    "inflammation": "body swelling and irritation",
    "lesion": "damaged tissue area",
    "ulcer": "open sore",
    "hemorrhage": "heavy bleeding",
    "infection": "harmful germs in the body",

    # =========================
    # MEDICATIONS & TREATMENTS
    # =========================
    "analgesic": "pain medicine",
    "antibiotic": "infection medicine",
    "antipyretic": "fever reducing medicine",
    "anticoagulant": "blood thinner",
    "antihistamine": "allergy medicine",
    "chemotherapy": "cancer treatment medicine",
    "radiotherapy": "radiation treatment",
    "dialysis": "machine-assisted blood cleaning",
    "intubation": "breathing tube insertion",
    "ventilation": "machine-assisted breathing",

    # =========================
    # BODY SYSTEM TERMS
    # =========================
    "renal": "kidney",
    "hepatic": "liver",
    "pulmonary": "lung",
    "cardiac": "heart",
    "neurological": "brain and nerve related",
    "dermatological": "skin related",
    "musculoskeletal": "muscle and bone related",
    "gastrointestinal": "digestive system related",

    # =========================
    # LAB & DIAGNOSTICS
    # =========================
    "hyperlipidemia": "high cholesterol",
    "leukocytosis": "high white blood cell count",
    "thrombocytopenia": "low platelet count",
    "elevated creatinine": "reduced kidney function marker",
    "positive biopsy": "test showing disease presence",
    "abnormal ecg": "irregular heart test result",
    "elevated liver enzymes": "possible liver damage indicators",

    # =========================
    # SURGICAL TERMS
    # =========================
    "laparotomy": "surgical opening of the abdomen",
    "appendectomy": "appendix removal surgery",
    "cholecystectomy": "gallbladder removal surgery",
    "biopsy": "tissue sample test",
    "resection": "surgical removal of tissue",
    "amputation": "removal of a body part",

    # =========================
    # PEDIATRIC / OBSTETRIC
    # =========================
    "preterm labor": "early childbirth",
    "gestational diabetes": "diabetes during pregnancy",
    "preeclampsia": "pregnancy-related high blood pressure",
    "neonatal jaundice": "yellowing in newborn babies",
    "fetal distress": "baby showing signs of stress before birth"
}

    def simplify_text(self, text):
        simplified = text.lower()

        # Replace medical jargon
        for medical_term, simple_term in self.medical_dictionary.items():
            simplified = re.sub(
                rf'\b{medical_term}\b',
                simple_term,
                simplified,
                flags=re.IGNORECASE
            )

        # Clean formatting: replace newlines with spaces and collapse multiple spaces
        simplified = simplified.replace("\n", " ")
        simplified = re.sub(r'\s+', ' ', simplified).strip()

        # Better capitalization: capitalize the first letter of each sentence
        sentences = simplified.split('. ')
        capitalized_sentences = [s.capitalize() for s in sentences]
        return ". ".join(capitalized_sentences)

    def generate_summary(self, text):
        simplified = self.simplify_text(text)

        summary = f"""
Summary:


{simplified}


"""

        return summary.strip()