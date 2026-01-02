from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

_ = load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str


@app.post("/api/generate_response")
def generate_response(request: PromptRequest):
    content = types.Content(
            role="user",
            parts=[types.Part(text=request.prompt)]
        )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content
    )

    return {"text": response.text}
