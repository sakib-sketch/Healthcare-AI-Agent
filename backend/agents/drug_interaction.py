from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class DrugInteractionAgent(BaseAgent):
    """
    Checks a list of medications for dangerous drug-drug interactions,
    contraindications, and allergy alerts.
    """

    def __init__(self):
        super().__init__()
        self.prompt_template = """
You are a Senior Clinical Pharmacist and Drug Safety Expert.

A patient is currently prescribed the following medications:
Medications: {medications}

Patient Conditions/Diagnoses: {conditions}
Patient Allergies: {allergies}
Patient Age/Gender: {demographics}

Your task is to:
1. Identify ALL significant drug-drug interactions between the listed medications.
2. Flag any contraindications given the patient's conditions.
3. Check for allergy conflicts.
4. Rate the severity of each finding.

Severity Levels:
- SEVERE: Life-threatening, requires immediate medication change.
- MODERATE: Significant risk, requires monitoring or dose adjustment.
- MINOR: Low risk, clinically insignificant but worth noting.

Output format must be a JSON object:
{{
    "overall_safety": "Safe / Caution / Danger",
    "total_interactions": 0,
    "interactions": [
        {{
            "drug_1": "Drug Name",
            "drug_2": "Drug Name",
            "severity": "SEVERE / MODERATE / MINOR",
            "effect": "Clinical description of the interaction effect",
            "recommendation": "What the clinician should do",
            "mechanism": "Brief pharmacological mechanism"
        }}
    ],
    "contraindications": [
        {{
            "drug": "Drug Name",
            "condition": "Condition it conflicts with",
            "severity": "SEVERE / MODERATE / MINOR",
            "recommendation": "Clinical recommendation"
        }}
    ],
    "allergy_alerts": [
        {{
            "drug": "Drug Name",
            "allergen": "Allergy it conflicts with",
            "recommendation": "Alternative or action"
        }}
    ],
    "safe_medications": ["list of medications with no identified issues"]
}}
Return ONLY the JSON. No other text.
"""

    def check(self, medications, conditions="", allergies="", demographics=""):
        if not medications:
            return {
                "overall_safety": "Safe",
                "total_interactions": 0,
                "interactions": [],
                "contraindications": [],
                "allergy_alerts": [],
                "safe_medications": []
            }

        prompt = self.prompt_template.format(
            medications=medications,
            conditions=conditions if conditions else "None specified",
            allergies=allergies if allergies else "No known allergies",
            demographics=demographics if demographics else "Not specified"
        )
        response = self.generate_response(prompt)
        default_fallback = {
            "overall_safety": "Safe",
            "total_interactions": 0,
            "interactions": [],
            "contraindications": [],
            "allergy_alerts": [],
            "safe_medications": []
        }
        return clean_and_parse_json(response, default_fallback=default_fallback)
