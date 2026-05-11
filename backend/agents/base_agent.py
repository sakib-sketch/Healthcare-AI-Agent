import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(override=True)

class BaseAgent:
    def __init__(self, model_name=None):
        self.api_key = os.getenv("COHERE_API_KEY")
        self.model_name = model_name or os.getenv("MODEL_NAME", "command-a-03-2025")
        
        if not self.api_key:
            raise ValueError("COHERE_API_KEY not found in environment variables.")
            
        self.llm = ChatCohere(
            model=self.model_name,
            cohere_api_key=self.api_key,
            temperature=0.1
        )

    def generate_response(self, prompt_text):
        response = self.llm.invoke(prompt_text)
        return response.content
