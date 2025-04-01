from groq import Groq
import os
import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables from .env file
load_dotenv()

class GroqLLM:
    def __init__(self, model_name="deepseek-r1-distill-llama-70b"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in config/.env.")
        
        # Initialize Groq client with minimal arguments
        try:
            self.client = Groq(api_key=api_key)
        except TypeError as e:
            print(f"Error initializing Groq client: {e}")
            raise
        self.last_call_time = 0

    def __call__(self, messages, temperature=0.7, max_tokens=1024):
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        if time_since_last < 20:
            time.sleep(20 - time_since_last)

        formatted_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                formatted_messages.append({"role": "system", "content": msg.content})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            self.last_call_time = time.time()
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            raise