from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from app.tools import web_search

_ = load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)

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

    config = types.GenerateContentConfig(
        tools=[web_search],
        system_instruction="You are a stock researcher with live web access. Use the web_search tool to find information for the stock provided. End your reponse with a recommendation on whether now would be a good time to buy the stock or not."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content,
        config=config
    )

    return {"text": response.text}
