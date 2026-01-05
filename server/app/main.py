import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from app.tools import web_search
import yfinance as yf

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

def generate_graphs(company):
    stock_prompt = f"""
        Return the stock ticker for {company}. Return JUST the stock ticker and nothing else.
    """

    stock_content = types.Content(
            role="user",
            parts=[types.Part(stock_prompt)]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=stock_content
    )

    df = yf.Ticker(response.text).history()

    path = r"C:\Users\damon\Documents\market-research-agent\client\images"

    graph_prompt = f"""
        Your job is to generate Python code to create three stock price line graphs (1 Day, 5 Days, and 1 Month) using a pre-existing pandas DataFrame named 'df'.
        
        DATASET SCHEMA:
        - Index: "Date" (Datetime objects, potentially timezone-aware)
        - Columns: "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"

        INSTRUCTIONS:
        1. **Backend**: You MUST use `matplotlib.use('Agg')` immediately after importing matplotlib to prevent GUI thread errors.
        2. **Filtering**: Use the 'Date' index to filter the last 1 day, 5 days, and 1 month of data from 'df' respectively.
        3. **Plotting**: 
        - Plot the "Close" price for each period.
        - Include a title, xlabel ('Date'), and ylabel ('Price').
        - Add a grid for readability.
        4. **Saving**: Save the files as "1D-Graph.png", "5D-Graph.png", and "1M-Graph.png" in the directory: {path}. Use `plt.savefig()` and overwrite existing files.
        5. **Cleanup**: Call `plt.close('all')` after saving to prevent memory leaks.
        
        CONSTRAINTS:
        - DO NOT use `plt.show()`.
        - DO NOT include any conversational text or explanations.
        - Wrap all code inside <executePython></executePython> tags.
        - Include all necessary imports (matplotlib, pandas, etc.).
        - Use absolute paths for saving by joining the directory {path} with the filenames.

        Only return the code inside the tags.
    """
    
    graph_content = types.Content(
            role="user",
            parts=[types.Part(text=graph_prompt)]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=graph_content
    )

    pattern = r"<executePython>([\s\S]*?)</executePython>"

    matched = re.search(pattern, response.text)

    python_code = matched.group(1).strip()

    code_text_path = r"C:\Users\damon\Documents\market-research-agent\server\llm-code.txt"

    with open(code_text_path, "w") as file:
        file.write(python_code)

    exec(python_code)




@app.post("/api/generate_response")
def generate_response(request: PromptRequest):
    generate_graphs(request.prompt)
    
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
