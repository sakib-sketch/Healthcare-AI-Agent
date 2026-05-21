from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class TreatmentRecommendationAgent(BaseAgent):
    """
    Recommends evidence-based treatment protocols for confirmed or suspected diagnoses,
    including medications, investigations, referrals, and follow-up timelines.
    """

    def __init__(self):
        super().__init__()
        self.prompt_template = """
You are a Senior Clinical Consultant following evidence-based medicine guidelines (WHO, NICE, AHA, ADA, etc.).

Patient Information:
Diagnoses / Suspected Conditions: {diagnoses}
Current Medications: {medications}
Patient History: {history}
Patient Demographics: {demographics}

Your task is to provide a complete, structured Treatment Plan for each diagnosis.

For each diagnosis provide:
1. First-line treatment (preferred medications with dosage guidelines)
2. Alternative treatments (if first-line is contraindicated)
3. Required investigations (labs, imaging, tests to order now)
4. Specialist referrals needed
5. Patient lifestyle / non-pharmacological recommendations
6. Follow-up timeline
7. Treatment goals / expected outcomes

Output format must be a JSON array:
[
    {{
        "diagnosis": "Diagnosis Name",
        "urgency": "Routine / Urgent / Emergency",
        "first_line_treatment": [
            {{
                "medication": "Drug name",
                "dose": "Dosage and frequency",
                "duration": "Treatment duration",
                "notes": "Special instructions"
            }}
        ],
        "alternative_treatment": [
            {{
                "medication": "Drug name",
                "dose": "Dosage and frequency",
                "reason": "Why to use this alternative"
            }}
        ],
        "investigations": [
            {{
                "test": "Test name",
                "reason": "Why this test is needed",
                "priority": "Immediate / Within 24h / Routine"
            }}
        ],
        "referrals": ["Specialist type and reason"],
        "lifestyle_recommendations": ["recommendation1", "recommendation2"],
        "follow_up": "Follow-up timeline and what to monitor",
        "treatment_goals": "Expected outcomes and success criteria",
        "guideline_source": "Guideline reference (e.g. WHO 2023, ADA 2024)"
    }}
]
Return ONLY the JSON array. No other text.
"""

    def recommend(self, diagnoses, medications="", history="", demographics=""):
        if not diagnoses:
            return []

        prompt = self.prompt_template.format(
            diagnoses=diagnoses,
            medications=medications if medications else "None reported",
            history=history if history else "No prior history provided",
            demographics=demographics if demographics else "Not specified"
        )
        response = self.generate_response(prompt)
        return clean_and_parse_json(response, default_fallback=[])
