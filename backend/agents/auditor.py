from .base_agent import BaseAgent
import json

class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a Senior Medical Auditor.
        Your task is to verify if the suggested ICD-10 codes accurately match the original clinical clinical notes.

        Original Clinical Note:
        {clinical_note}

        Suggested Codes:
        {suggested_codes}

        For each code, provide:
        1. A "status" (Approved/Rejected/Need Review)
        2. A "confidence_score" (0.0 to 1.0)
        3. A "reason" for your decision.

        Output format must be a JSON array:
        [
            {{
                "icd10_code": "CODE",
                "status": "Approved",
                "confidence_score": 0.95,
                "reason": "Perfect match for the diagnosis mentioned."
            }}
        ]
        Return ONLY the JSON. No other text.
        """

    def audit(self, note, codes):
        if not codes:
            return []
        
        prompt = self.prompt_template.format(clinical_note=note, suggested_codes=str(codes))
        response = self.generate_response(prompt)
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            json_data = response[start:end]
            return json.loads(json_data)
        except Exception as e:
            return {"error": f"Failed to audit codes: {str(e)}", "raw_response": response}
