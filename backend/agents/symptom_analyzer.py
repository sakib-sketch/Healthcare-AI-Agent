from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class SymptomAnalysisAgent(BaseAgent):
    """
    Analyzes patient symptoms and history to generate a ranked
    differential diagnosis list with confidence scores and red flags.
    """

    def __init__(self):
        super().__init__()
        self.prompt_template = """
You are a highly experienced Clinical Diagnostician and Medical AI Assistant.

A patient presents with the following information:

Patient Symptoms: {symptoms}
Patient Medical History: {history}
Current Medications: {medications}
Patient Age/Gender: {demographics}

Your task is to generate a ranked Differential Diagnosis list.

Rules:
1. List the TOP 5 most likely diagnoses ranked by probability (most likely first).
2. For each diagnosis, provide a confidence percentage (0-100%).
3. List key supporting symptoms that point to this diagnosis.
4. List any RED FLAG symptoms that require URGENT attention.
5. Suggest the most critical next diagnostic step for each.

Output format must be a JSON array:
[
    {{
        "rank": 1,
        "diagnosis": "Diagnosis Name",
        "icd10_code": "ICD-10 code if known",
        "confidence": 85,
        "supporting_symptoms": ["symptom1", "symptom2"],
        "red_flags": ["red flag if any, else empty list"],
        "next_step": "Most important next diagnostic action",
        "urgency": "Routine / Urgent / Emergency"
    }}
]
Return ONLY the JSON array. No other text.
"""

    def analyze(self, symptoms, history="", medications="", demographics=""):
        prompt = self.prompt_template.format(
            symptoms=symptoms,
            history=history if history else "No prior history provided",
            medications=medications if medications else "None reported",
            demographics=demographics if demographics else "Not specified"
        )
        response = self.generate_response(prompt)
        return clean_and_parse_json(response, default_fallback=[])
