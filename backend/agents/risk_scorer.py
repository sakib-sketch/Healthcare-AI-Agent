from .base_agent import BaseAgent
from .json_parser import clean_and_parse_json

class RiskScoringAgent(BaseAgent):
    """
    Calculates patient risk scores including overall severity,
    readmission risk, sepsis risk flag, and critical condition alerts.
    """

    def __init__(self):
        super().__init__()
        self.prompt_template = """
You are a Clinical Risk Assessment Specialist with expertise in predictive patient outcomes.

Patient Information:
Diagnoses / Conditions: {diagnoses}
Symptoms: {symptoms}
Medications: {medications}
Patient History: {history}
Patient Demographics: {demographics}
Vitals (if available): {vitals}

Your task is to perform a comprehensive clinical risk assessment.

Assess the following:
1. Overall clinical severity level (Low / Medium / High / Critical)
2. 30-day hospital readmission risk percentage
3. Sepsis risk flag (Yes / No / Possible) with reasoning
4. Mortality risk (Low / Moderate / High)
5. Key risk factors driving the assessment
6. Immediate action items for the clinical team
7. Monitoring parameters to watch closely

Output format must be a JSON object:
{{
    "overall_severity": "Low / Medium / High / Critical",
    "severity_score": 0,
    "severity_color": "green / yellow / orange / red",
    "readmission_risk_pct": 0,
    "readmission_category": "Low / Moderate / High",
    "sepsis_flag": "Yes / No / Possible",
    "sepsis_reasoning": "Brief explanation",
    "mortality_risk": "Low / Moderate / High",
    "key_risk_factors": ["factor1", "factor2"],
    "immediate_actions": [
        {{
            "action": "Action description",
            "priority": "Immediate / Within 1h / Within 24h"
        }}
    ],
    "monitoring_parameters": [
        {{
            "parameter": "What to monitor (e.g., Blood Pressure, SpO2)",
            "frequency": "How often to check",
            "alert_threshold": "When to escalate"
        }}
    ],
    "clinical_notes": "Overall narrative summary of risk assessment"
}}
Return ONLY the JSON. No other text.
"""

    def score(self, diagnoses, symptoms="", medications="", history="", demographics="", vitals=""):
        prompt = self.prompt_template.format(
            diagnoses=diagnoses if diagnoses else "Not specified",
            symptoms=symptoms if symptoms else "Not specified",
            medications=medications if medications else "None reported",
            history=history if history else "No prior history",
            demographics=demographics if demographics else "Not specified",
            vitals=vitals if vitals else "Not provided"
        )
        response = self.generate_response(prompt)
        default_fallback = {
            "overall_severity": "Unknown",
            "severity_score": 0,
            "severity_color": "grey",
            "readmission_risk_pct": 0,
            "readmission_category": "Unknown",
            "sepsis_flag": "No",
            "sepsis_reasoning": "Could not assess",
            "mortality_risk": "Unknown",
            "key_risk_factors": [],
            "immediate_actions": [],
            "monitoring_parameters": [],
            "clinical_notes": "Risk scoring failed due to a parsing error."
        }
        return clean_and_parse_json(response, default_fallback=default_fallback)

