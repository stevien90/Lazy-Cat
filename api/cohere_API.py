import cohere
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET")    
co = cohere.ClientV2(api_key=api_key)

def get_cohere_response(user_input: str) -> str:
    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": user_input}],
    )
    assistant_message = response.message
    if assistant_message and assistant_message.content:
        for item in assistant_message.content:
            if getattr(item, "type", None) == "text":
                return item.text
    return ""

