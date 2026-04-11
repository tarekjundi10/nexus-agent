import os
from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import requests
from bs4 import BeautifulSoup

api_key = os.getenv("OPENAI_API_KEY")
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=api_key)

def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily and return top results."""
    try:
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def summarize_url(url: str) -> str:
    """Fetch a webpage and summarize its content using the LLM."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)[:4000]

        summary = llm.invoke([
            HumanMessage(content=f"Summarize the following article in 3-5 key points:\n\n{text}")
        ])
        return summary.content
    except Exception as e:
        return f"Could not summarize URL: {str(e)}"


def synthesize_findings(goal: str, findings: list[dict]) -> str:
    """Synthesize all search findings into a structured research report."""
    findings_text = ""
    for i, f in enumerate(findings):
        findings_text += f"\n\nSource {i+1}: {f.get('title', '')}\n"
        findings_text += f"URL: {f.get('url', '')}\n"
        findings_text += f"Content: {f.get('content', '')}\n"

    prompt = f"""You are an expert research analyst. Based on the following research findings, write a comprehensive, structured report for the goal: "{goal}"

The report must include:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Conclusions and Recommendations
5. Sources

Research Findings:
{findings_text}

Write in a professional, clear, and concise manner."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


if __name__ == "__main__":
    results = web_search("AI trends in healthcare 2024")
    for r in results:
        print(r["title"])
        print(r["url"])
        print()