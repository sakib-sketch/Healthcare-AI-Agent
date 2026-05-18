import re

class HumanizerAgent:
    """
    Converts complex clinical notes into simple human-readable summaries.
    """

    def __init__(self):
        self.medical_dictionary = {
            "hypertension": "high blood pressure",
            "diabetes mellitus": "diabetes",
            "myocardial infarction": "heart attack",
            "dyspnea": "difficulty breathing",
            "edema": "swelling",
            "neuropathy": "nerve damage",
            "ulcer": "open sore",
            "tachycardia": "fast heart rate",
            "bradycardia": "slow heart rate",
            "fracture": "broken bone",
            "carcinoma": "cancer",
            "benign": "non-cancerous",
            "malignant": "cancerous",
            "analgesic": "pain medicine",
            "antibiotic": "infection medicine",
            "renal": "kidney",
            "pulmonary": "lung",
            "hepatic": "liver",
            "cardiac": "heart"
        }

    def simplify_text(self, text):
        simplified = text.lower()

        # Replace medical jargon
        for medical_term, simple_term in self.medical_dictionary.items():
            simplified = re.sub(
                rf'\b{medical_term}\b',
                simple_term,
                simplified,
                flags=re.IGNORECASE
            )

        # Clean formatting: replace newlines with spaces and collapse multiple spaces
        simplified = simplified.replace("\n", " ")
        simplified = re.sub(r'\s+', ' ', simplified).strip()

        # Better capitalization: capitalize the first letter of each sentence
        sentences = simplified.split('. ')
        capitalized_sentences = [s.capitalize() for s in sentences]
        return ". ".join(capitalized_sentences)

    def generate_summary(self, text):
        simplified = self.simplify_text(text)

        summary = f"""
Patient-Friendly Summary:

The patient report indicates the following:

{simplified}

This summary is generated to help non-medical users understand the clinical content more easily.
"""

        return summary.strip()