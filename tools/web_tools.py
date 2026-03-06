from langchain.tools import tool
from tavily import TavilyClient
import os

client = TavilyClient(api_key="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")

@tool
def web_search(query: str):
    """
    Search the web for general information using Tavily AI search.

    Use this tool when the user asks about:
    - General knowledge questions
    - Definitions or explanations
    - Recent events
    - Information about people, companies, technologies, or places

    Input:
        query (str): Search query.

    Returns:
        dict: Contains summarized answer and top sources.
    """

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    return {
        "answer": response.get("answer"),
        "results": [
            {
                "title": r["title"],
                "url": r["url"],
                "content": r["content"]
            }
            for r in response.get("results", [])
        ]
    }