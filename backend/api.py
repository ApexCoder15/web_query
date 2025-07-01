from langgraph_agents import graph
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputText(BaseModel):
    query: str

@app.post("/query")
async def process_text(input_data: InputText):
    input_str = input_data.query
    initial_state = {"query": input_str}
    final_state = await graph.ainvoke(initial_state)
    ret_str = ""

    if not final_state.get("is_valid"):
        ret_str = "Query is not valid for search."
    elif final_state.get("cached_summary"):
        ret_str = final_state["cached_summary"]
    else:
        ret_str = final_state["summary"]
    return {"result": ret_str}

