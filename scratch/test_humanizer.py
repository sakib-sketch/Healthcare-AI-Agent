import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from agents.humanizer_agent import HumanizerAgent

agent = HumanizerAgent()
note = """
Patient has Hypertension and Diabetes Mellitus. 
Experience Dyspnea and Edema.
"""
print("Original Note:")
print(note)
print("\nSimplified Text:")
print(agent.simplify_text(note))
print("\nGenerated Summary:")
print(agent.generate_summary(note))
