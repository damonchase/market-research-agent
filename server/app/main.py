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
import re
import os
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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

IMAGES_DIR = os.path.join(os.getcwd(), "images")
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

class PromptRequest(BaseModel):
    prompt: str

def extract_json(text):
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def get_base64(period):
            path = os.path.join(IMAGES_DIR, f"{period}.png")
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')


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
        
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], color='purple', linewidth=2)
        
        plt.title(f"{ticker} - {period_name} Analysis", fontsize=14)
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        img_path = os.path.join(IMAGES_DIR, f"{period_name}.png")
        plt.savefig(img_path)
        plt.close()
        
@app.post("/api/generate_response")
def generate_response(request: PromptRequest):
    ai_instruction = f"""
            You are a Senior Equity Research Analyst. Your goal is to provide deep, data-driven insights into stocks.

            ### OPERATIONAL RULES:
            1. **Web Search:** Always use the `web_search` tool to get the latest stock price, recent news (last 7 days), and quarterly earnings data.
            2. **Analysis:** Evaluate the stock based on:
                - Recent price action and momentum.
                - Key fundamental catalysts (earnings, product launches).
                - Market sentiment and analyst ratings.
            3. **Recommendation:** Conclude with a clear "Buy", "Hold", or "Sell" rating with a 1-sentence justification.

            ### OUTPUT FORMAT:
            You must return ONLY a valid JSON object. Use Markdown formatting (headers, bolding, lists) within the "text" field to ensure the response is scannable.

            JSON Structure:
            {{
                "ticker": "STRING (Uppercase)",
                "text": "STRING (Markdown formatted research report)"
            }}
            """
    
    config = types.GenerateContentConfig(
        tools=[web_search],
        system_instruction=ai_instruction
    )

    content = types.Content(
            role="user",
            parts=[types.Part(text=request.prompt)]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content,
        config=config
    )

    

    try:
        json_response = json.loads(extract_json(response.text))
        print(f"Response ======================\n{json_response["text"]}")
        generate_graphs(json_response["ticker"])

        return {
            "text": json_response["text"],
            "image_data1": f"data:image/png;base64,{get_base64('5d')}",
            "image_data2": f"data:image/png;base64,{get_base64('1mo')}",
            "image_data3": f"data:image/png;base64,{get_base64('6mo')}"
        }
        
    except Exception as e:
        import traceback
        print(traceback.format_exc()) 
        return {"text": f"Error: {str(e)}"} 