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
import kaleido

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

def extract_json(text):
    # Use regex to find everything between the first { and the last }
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def generate_graphs(ticker):
    company = yf.Ticker(ticker)

    full_history = company.history(period="6mo", interval="1d").round({'Close': 2})
    
    if full_history.empty:
        print(f"No data found for {ticker}")
        return

    df_list = [
        {"df": full_history.tail(5), "period": "5d"},
        {"df": full_history.tail(21), "period": "1mo"},
        {"df": full_history, "period": "6mo"}
    ]

    for item in df_list:
        data = item["df"]
        period = item["period"]
        
        fig1 = px.line(
            data,
            x=data.index,
            y="Close",
            title=f"{ticker} - {period} Analysis",
            labels={"Close": "Price (USD)", "Date": "Date"},
            color_discrete_sequence=['purple']
        )
        
        img_path = fr".\images\{period}.png"
        fig1.write_image(img_path)

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
        You must return ONLY a valid JSON object in plain text so that it could be converted to a json object in python using the json.loads() function, so make sure your output would be compatable.
        Use Markdown formatting (headers, bolding, lists) within the "text" field to ensure the response is scannable.

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

    raw_text = response.text


    try:
        clean_json = extract_json(raw_text)
        parsed_response = json.loads(clean_json)  
        generate_graphs(parsed_response["ticker"])

        with open("./images/5d.png", "rb") as image_file:
            encoded_string1 = base64.b64encode(image_file.read()).decode('utf-8')
        with open("./images/1mo.png", "rb") as image_file2:
            encoded_string2 = base64.b64encode(image_file2.read()).decode('utf-8')
        with open("./images/6mo.png", "rb") as image_file3:
            encoded_string3 = base64.b64encode(image_file3.read()).decode('utf-8')
        
        print(f"DEBUG: Text length is {len(str(parsed_response["text"]))}")
        print(f"DEBUG: Content is {parsed_response["text"]}")

        return {"text": parsed_response["text"],
                "image_data1": f"data:image/png;base64,{encoded_string1}",
                "image_data2": f"data:image/png;base64, {encoded_string2}",
                "image_data3": f"data:image/png;base64, {encoded_string3}"}
        
    except Exception as e:
        return {"text": e}
