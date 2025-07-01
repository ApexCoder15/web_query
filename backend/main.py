from langgraph_agents import graph
import asyncio

async def run():
    while True:
        query = input("Enter Your query: ")
        if query.lower() == "end":
            break
        initial_state = {"query": query}
        final_state = await graph.ainvoke(initial_state)

        if not final_state.get("is_valid"):
            print("❌ Query is not valid for search.")
        elif final_state.get("cached_summary"):
            print("⚡ Returning cached result:\n")
            print(final_state["cached_summary"])
        else:
            print("✅ Fresh result from search:\n")
            print(final_state["summary"])

if __name__ == "__main__":
    asyncio.run(run())