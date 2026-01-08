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

def generate_graphs(ticker):
    company = yf.Ticker(ticker)

    df5d = company.history(period="5d", interval="1d").round({'Close': 2})
    df1mo = company.history(period="1mo", interval="1d").round({'Close': 2})
    df6mo = company.history(period="6mo", interval="1d").round({'Close': 2})

    df_list = [{"df": df5d, "period": "5d"}, {"df": df1mo, "period": "1mo"}, {"df": df6mo, "period": "6mo"}]

    for df in df_list:
        data = df["df"]
        period = df["period"]
        fig1 = px.line(
            data,
            x=data.index,
            y="Close",
            title=f"{company.info['longName']}",
            labels={"Close": "Price (USD)", "index": "Date"},
            color_discrete_sequence=['purple']
        )
        fig1.write_image(f"C:\Users\damon\Documents\market-research-agent\client\public\images\{period}.png") 




@app.post("/api/generate_response")
def generate_response(request: PromptRequest):
    content = types.Content(
            role="user",
            parts=[types.Part(text=request.prompt)]
    )

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content,
        config=config
    )

    parsed_response = json.loads(response.text)

    generate_graphs(parsed_response["ticker"])

    return {"text": parsed_response["text"]}
