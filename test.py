from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='config/.env')
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key}")
client = Groq(api_key=api_key)
print("Groq client initialized successfully")