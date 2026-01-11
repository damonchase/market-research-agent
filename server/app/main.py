import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from app.tools import web_search
import yfinance as yf
import json
import plotly.express as px
import re
import os
import yfinance as yf
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
import typing_extensions as typing


_ = load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)

app = FastAPI()

origins = [
    "http://localhost:3000",  # Local
    "https://market-research-agent-rosy.vercel.app",  # Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class ResearchReport(typing.TypedDict):
    ticker: str
    text: str

def extract_json(text):
    # Use regex to find everything between the first { and the last }
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

IMAGES_DIR = os.path.join(os.getcwd(), "images")
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def generate_graphs(ticker):
    company = yf.Ticker(ticker)
    full_history = company.history(period="6mo", interval="1d").round({'Close': 2})
    
    if full_history.empty:
        print(f"No data found for {ticker}")
        return

    periods = [
        {"data": full_history.tail(5), "name": "5d"},
        {"data": full_history.tail(21), "name": "1mo"},
        {"data": full_history, "name": "6mo"}
    ]

    for item in periods:
        data = item["data"]
        period_name = item["name"]
        
        # Create the plot
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], color='purple', linewidth=2)
        
        # Styling
        plt.title(f"{ticker} - {period_name} Analysis", fontsize=14)
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save the image (Uses standard OS paths we discussed)
        img_path = os.path.join(IMAGES_DIR, f"{period_name}.png")
        plt.savefig(img_path)
        plt.close() # Important: Close the plot to free up memory
        
@app.post("/api/generate_response")
def generate_response(request: PromptRequest):
    content = types.Content(
            role="user",
            parts=[types.Part(text=request.prompt)]
    )

    ai_instruction = """
    You are a Senior Equity Research Analyst.

    ### OUTPUT RULES:
    1. Return ONLY a valid JSON object.
    2. The "text" field MUST contain the Markdown report.
    3. Use standard JSON string escaping (e.g., " for quotes, \n for newlines). 
    4. Do not include markdown code blocks (like ```json) in your response.

    Structure:
    {
        "ticker": "TICKER",
        "text": "MARKDOWN_CONTENT"
    }
    """    
    config = types.GenerateContentConfig(
        tools=[web_search],
        system_instruction="You are a Senior Equity Research Analyst. Provide deep, data-driven insights.",
        response_mime_type="application/json",
        response_schema=ResearchReport, # Forces the AI to follow your dictionary structure
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash", # Use 2.0 or 1.5 for best schema support
        contents=content,
        config=config
    )



    try:
        parsed_response = json.loads(response.text) 
        
        # This will now save to /opt/render/project/src/server/images/ on Render
        generate_graphs(parsed_response["ticker"])

        # 3. Use the global IMAGES_DIR variable for reading
        def get_base64(period):
            path = os.path.join(IMAGES_DIR, f"{period}.png")
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')

        return {
            "text": parsed_response["text"],
            "image_data1": f"data:image/png;base64,{get_base64('5d')}",
            "image_data2": f"data:image/png;base64,{get_base64('1mo')}",
            "image_data3": f"data:image/png;base64,{get_base64('6mo')}"
        }
        
    except Exception as e:
        import traceback
        print(traceback.format_exc()) 
        return {"text": f"Error: {str(e)}"} 