from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a highly accurate Medical Information Extractor. 
        Your task is to read clinical notes and extract specific medical entities.
        
        Extract the following:
        1. Diagnosis (Diseases or conditions mentioned)
        2. Symptoms (Complaints from the patient)
        3. Procedures (Tests, surgeries, or treatments performed)
        4. Medications (Drugs prescribed)

        Clinical Note:
        {clinical_note}

        Output format must be a clean JSON object like this:
        {{
            "diagnosis": [],
            "symptoms": [],
            "procedures": [],
            "medications": []
        }}
        Return ONLY the JSON. No other text.
        """

    def extract(self, note):
        prompt = self.prompt_template.format(clinical_note=note)
        response = self.generate_response(prompt)
        default_fallback = {
            "diagnosis": [],
            "symptoms": [],
            "procedures": [],
            "medications": []
        }
        return clean_and_parse_json(response, default_fallback=default_fallback)
