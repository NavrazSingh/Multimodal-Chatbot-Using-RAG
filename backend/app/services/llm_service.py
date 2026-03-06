import os
from groq import Groq
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables.")
            raise ValueError("GROQ_API_KEY is required.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile" # Llama-3.3-70B

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            return "I'm sorry, I encountered an error while generating a response."
