from tavily import TavilyClient
from dotenv import load_dotenv
import os

_ = load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key=tavily_api_key)

def web_search(query: str) -> str:
    """
    Performs a live web search using Tavily to get up-to-date information.
    Args:
        query: The search string to look up on the internet.
    """
    response = tavily.search(query=query, search_depth="basic")
    
    # Format the results into a string for the model to read
    results = [f"Source: {r['url']}\nContent: {r['content']}" for r in response['results']]
    print(query)
    return "\n\n".join(results)