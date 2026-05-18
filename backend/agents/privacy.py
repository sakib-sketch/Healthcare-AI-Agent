from .base_agent import BaseAgent

class PrivacyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_template = """
        You are a strict HIPAA Compliance Officer and Data Privacy Expert.
        Your task is to scan the provided clinical note and redact ALL Protected Health Information (PHI) to ensure patient privacy.
        
        You must replace the following types of information with redaction tags:
        1. Patient Names -> [REDACTED_NAME]
        2. Specific Dates (e.g., DOB, visit date) -> [REDACTED_DATE]
        3. Phone Numbers -> [REDACTED_PHONE]
        4. Addresses -> [REDACTED_ADDRESS]
        5. Social Security Numbers or IDs -> [REDACTED_ID]
        
        DO NOT redact medical conditions, symptoms, procedures, or medications. Those are needed for coding.
        
        Original Clinical Note:
        {clinical_note}
        
        Return ONLY the fully anonymized and redacted text. No introductory sentences, no formatting outside of the redacted tags.
        """

    def anonymize(self, note):
        if not note or note.strip() == "":
            return note
            
        prompt = self.prompt_template.format(clinical_note=note)
        response = self.generate_response(prompt)
        return response.strip()
