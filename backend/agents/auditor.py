from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a Senior Medical Compliance Auditor.
        Your task is to verify if the suggested medical codes (ICD-10 and CPT) accurately match the original clinical clinical notes.

        Original Clinical Note:
        {clinical_note}

        Suggested Codes:
        {suggested_codes}

        For each code, provide:
        1. A "status" (Approved/Rejected/Need Review)
        2. A "confidence_score" (0.0 to 1.0)
        3. A "medical_necessity": (Yes/No) - Does the diagnosis justify this procedure?
        4. A "reason": Detailed explanation of your decision.

        Output format must be a JSON array of objects:
        [
            {{
                "code": "CODE",
                "status": "Approved",
                "confidence_score": 0.95,
                "medical_necessity": "Yes",
                "reason": "Perfect match for the diagnosis and procedure mentioned."
            }}
        ]
        Return ONLY the JSON. No other text.
        """

    def audit(self, note, codes):
        if not codes:
            return []
        
        prompt = self.prompt_template.format(clinical_note=note, suggested_codes=str(codes))
        response = self.generate_response(prompt)
        return clean_and_parse_json(response, default_fallback=[])
