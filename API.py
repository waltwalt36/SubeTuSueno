import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

messages = [
    {
        "role": "system",
        "content": (
            "You are an assistant helping first-generation college students with questions about applying to college. "
            "Explain topics in simple terms as if you are talking to someone who has no prior knowledge of the subject. "
            "Use clear and concise language, avoid jargon, and provide examples where necessary."
        )
    }
]

def chatbot_response(user_input):
    try:
        messages.append({"role": "user", "content": user_input})
        # Call OpenAI's GPT model
        response = openai.chat.completions.create(# openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=messages
        )
        #chatbot_response = response['choices'][0]['message']['content']
        chatbot_response = response.choices[0].message.content
        # Extract and return the chatbot's reply
        messages.append({"role": "assistant", "content": chatbot_response})
        return chatbot_response
        
    except Exception as e:
        return f"Error: {str(e)}"