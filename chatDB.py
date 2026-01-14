from dotenv import load_dotenv
from base_prompt import BasePrompt
from chatGemini import Gemini,ChatResponse
from typing import Optional
load_dotenv()

models = ["gemini-3-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-flash-preview-09-2025","gemini-2.5-flash-lite"]

class ChatDB:
    def __init__(self,key:str,tab_details) -> None:
        self.key = key
        self.base_prompt = BasePrompt(table_details=tab_details)

    def chat(self,inp:str)->str|Exception:
        gemini = Gemini(api_key=self.key)
        query = {}
        try:
            for model in models:
                print(f"Using model {model}...")
                query['model'] = model
                query['query'] = inp
                query['base_prompt'] = self.base_prompt()

                response = gemini.chat(query)

                if response.response:
                    return response.response.text
                if response.error_type in {
                    "MODEL_ACCESS_DENIED",
                    "MODEL_NOT_FOUND",
                    "QUOTA_EXCEEDED"
                }:
                    continue

                raise RuntimeError(response.error)

            raise RuntimeError("No available Gemini model succeeded")
        except Exception as e:
            raise Exception(e)

