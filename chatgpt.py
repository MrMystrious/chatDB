from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()
key = os.getenv("GPT_API_KEY")
client = OpenAI(api_key=key)

response = client.responses.create(
    model="gpt-5.2",
    input="Explain me how to use openai api for chatgpt"

)
print(response.output_text)