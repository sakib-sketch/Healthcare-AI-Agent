from .base_agent import BaseAgent
import json

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a highly accurate Medical Information Extractor. 
        Your task is to read clinical notes and extract specific medical entities.
        
        Extract the following:
        1. Diagnoses (Diseases or conditions mentioned)
        2. Symptoms (Complaints from the patient)
        3. Procedures (Tests, surgeries, or treatments performed)
        4. Medications (Drugs prescribed)

        Clinical Note:
        {clinical_note}

        Output format must be a clean JSON object like this:
        {{
            "diagnoses": [],
            "symptoms": [],
            "procedures": [],
            "medications": []
        }}
        Return ONLY the JSON. No other text.
        """

    def extract(self, note):
        prompt = self.prompt_template.format(clinical_note=note)
        response = self.generate_response(prompt)
        try:
            # Simple cleaning in case the model adds extra text
            start = response.find('{')
            end = response.rfind('}') + 1
            json_data = response[start:end]
            return json.loads(json_data)
        except Exception as e:
            return {"error": f"Failed to parse extraction: {str(e)}", "raw_response": response}
