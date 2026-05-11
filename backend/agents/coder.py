from .base_agent import BaseAgent
import json

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a Certified Medical Coder (ICD-10-CM Expert).
        Your task is to take a list of medical diagnoses and map each one to its correct ICD-10 code and official description.

        Diagnoses List:
        {diagnoses}

        Output format must be a JSON array of objects:
        [
            {{
                "diagnosis": "Original diagnosis",
                "icd10_code": "CODE",
                "description": "Official ICD-10 Description"
            }}
        ]
        Return ONLY the JSON. No other text.
        """

    def map_codes(self, diagnoses):
        if not diagnoses:
            return []
        
        prompt = self.prompt_template.format(diagnoses=str(diagnoses))
        response = self.generate_response(prompt)
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            json_data = response[start:end]
            return json.loads(json_data)
        except Exception as e:
            return {"error": f"Failed to map codes: {str(e)}", "raw_response": response}
