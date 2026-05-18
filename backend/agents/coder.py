from .base_agent import BaseAgent
import json

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a Certified Medical Coder (ICD-10-CM and CPT Expert).
        Your task is to take a list of medical diagnoses and procedures and map each one to its correct code.

        Diagnoses: {diagnoses}
        Procedures: {procedures}

        Rules:
        1. For each Diagnosis, find the most accurate ICD-10-CM code.
        2. For each Procedure, find the most accurate CPT code (5 digits).
        3. Provide an official description for each code.

        Output format must be a JSON array of objects:
        [
            {{
                "entity": "Original text (diagnosis or procedure)",
                "type": "Diagnosis or Procedure",
                "code": "ICD-10 or CPT code",
                "description": "Official description"
            }}
        ]
        Return ONLY the JSON. No other text.
        """

    def map_codes(self, diagnoses, procedures):
        if not diagnoses and not procedures:
            return []
        
        prompt = self.prompt_template.format(
            diagnoses=str(diagnoses),
            procedures=str(procedures)
        )
        response = self.generate_response(prompt)
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            json_data = response[start:end]
            return json.loads(json_data)
        except Exception as e:
            return {"error": f"Failed to map codes: {str(e)}", "raw_response": response}
