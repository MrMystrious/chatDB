from google import genai
from google.genai.types import GenerateContentResponse
from dotenv import load_dotenv
from typing import Dict,Optional,TypedDict,Iterator
from dataclasses import dataclass

load_dotenv()

class ChatQuery(TypedDict):
    model:str
    query:str
    base_prompt:str

@dataclass
class ChatResponse:
    response : Optional[GenerateContentResponse]
    error : Optional[Exception]
    error_type : Optional[str]

class Gemini:
    def __init__(self,api_key=None) -> None:
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
    def chat(self,query:ChatQuery) -> ChatResponse:
        try:
            if query["model"] in ["gemini-2.5-flash","gemini-2.5-flash-preview-09-2025","gemini-2.5-flash-lite"]:
                content = {
                    "role":"user",
                    "parts":[
                        {
                            "text":f"{query['base_prompt']} \n\n User query :\n{query['query']}"
                        }
                    ]
                }
            else:
                content = [
                    {
                        "role":"system",
                        "parts":[{"text":query["base_prompt"]}]
                    },
                    {
                        "role":"user",
                        "parts":[{"text":query['query']}]
                    }
                ]
                
            if query['model'] and query["query"]:
                response = self.client.models.generate_content(
                    model=query["model"],
                    contents=content
                )
                #print("response",response)
                return ChatResponse(response=response,error=None,error_type=None)
            else:
                raise KeyError("model name or input contents is not found")
        except Exception as e:
            msg = str(e).lower()
            #print(msg,'\n\n')
            if "permission" in msg or "not authorized" in msg:
                etype = "MODEL_ACCESS_DENIED"
            elif "model not found" in msg:
                etype = "MODEL_NOT_FOUND"
            elif "quota" in msg or "exceeded" in msg:
                etype = "QUOTA_EXCEEDED"
            else:
                etype = "TRANSIENT_ERROR"

            return ChatResponse(response=None, error=str(e), error_type=etype)
    def chat_stream(self,query:ChatQuery) -> Iterator[GenerateContentResponse]:
        content = [
                {
                    "role":"system",
                    "parts":[{"text":query["base_prompt"]}]
                },
                {
                    "role":"user",
                    "parts":[{"text":query['query']}]
                }
            ]
        return self.client.models.generate_content_stream(
                model=query["model"],
                contents=content
            )
