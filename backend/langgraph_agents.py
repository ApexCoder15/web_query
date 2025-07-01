import asyncio
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from typing import TypedDict
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from search import screenshot_result
from db import search_similar_query, store_query_and_result
from ocr import get_text

# ---- Shared State ----
class AgentState(TypedDict):
    query: str
    is_valid: bool
    cached_summary: str
    search_results: str
    summary: str

load_dotenv()


llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

screenshot_path = "curr_img.png"
no_articles = 5

# ---- Node 1: Query Validator ----
def validate_query(state: AgentState) -> AgentState:
    prompt = f"Is the given query valid for web search? Reply 'Yes' if its a valid search query else 'No' and nothing else. For example: 'Walk my pet' or 'add apples to grocery' are not valid search query. So anything that sounds like a command is not a valid search query.\nQuery: {state['query']}"
    result = llm.predict(prompt).strip().lower()
    return {**state, "is_valid": result.startswith("yes")}

# ---- Node 2: Check Vector DB ----
def check_previous_queries(state: AgentState) -> AgentState:
    query = state["query"]
    cached = search_similar_query(query)
    if cached:
        return {**state, "cached_summary": cached}
    return state

# ---- Node 3: Web Search & Summarize ----
async def search_and_summarize(state: AgentState) -> AgentState:
    query = state["query"]
    content = ""
    count = 0
    for i in range(10):
        await screenshot_result(query, i, screenshot_path)
        curr_text = get_text(screenshot_path)
        if curr_text is not None:
            count += 1
            curr_summary = llm.predict(f"Summarize the following search results :\n\n{curr_text}")
            content += curr_summary
        if count == 4:
            break
    summary_prompt = f"Summarize the following search results :\n\n{content}"
    summary = llm.predict(summary_prompt)

    # Save to vector store
    store_query_and_result(query, summary)

    return {**state, "search_results": content, "summary": summary}

# ---- Routing Logic ----
def route_after_validation(state: AgentState) -> str:
    return "check_cache" if state["is_valid"] else END

def route_after_cache(state: AgentState) -> str:
    return END if state.get("cached_summary") else "search_and_summarize"

# ---- Graph Build ----
builder = StateGraph(AgentState)
builder.add_node("validate_query", validate_query)
builder.add_node("check_cache", check_previous_queries)
builder.add_node("search_and_summarize", search_and_summarize)

builder.set_entry_point("validate_query")
builder.add_conditional_edges("validate_query", route_after_validation)
builder.add_conditional_edges("check_cache", route_after_cache)
builder.add_edge("search_and_summarize", END)

graph = builder.compile()

