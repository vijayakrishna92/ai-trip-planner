# install required packages first:
# pip install langgraph langchain langchain-groq

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_ollama import ChatOllama
# import os
# from dotenv import load_dotenv
from typing import TypedDict
import logging
from langgraph.prebuilt import ToolNode
import re

logging.basicConfig(level=logging.DEBUG)

# load_dotenv()



# Step 1: Define a simple tool
@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    logging.debug(f"[TOOL] add_numbers called with a={a}, b={b}")
    return a + b

# Step 2: Initialize the LLM (using Groq)
#llm = ChatGroq(
#    model="llama-3.1-8b-instant",  # You can change this to another Groq-supported model
#    api_key=os.getenv("YOUR_GROQ_API_KEY"))
#llm_with_tools = llm.bind_tools([add_numbers])
llm = ChatOllama(model="llama3-groq-tool-use:8b")
llm_with_tools = llm.bind_tools([add_numbers])
# Step 3: Define a basic agent node
def agent_node(state: dict):
    user_input = state["input"]
    logging.debug(f"[NODE] agent_node received input: {user_input}")

    response = llm_with_tools.invoke(
        f"You are a helpful assistant. For the question: '{user_input}', "
        f"decide if you should call the add_numbers tool. "
        f"If yes, output: TOOL_CALL add_numbers with a=<value> b=<value>. "
        f"If no, simply answer the question."
    )

    logging.debug(f"[LLM] got response: {response}")

    text = response.content
    match = re.search(r"TOOL_CALL\s+add_numbers\s+with\s+a=(\d+)\s+b=(\d+)", text)
    if match:
        a, b = float(match.group(1)), float(match.group(2))
        result = add_numbers(a, b)
        state["output"] = f"The result is {result}"
    else:
        state["output"] = text

    return state
# def agent_node(state: dict):
#     """
#     This node reads the user input and produces a response using the Groq LLM.
#     """
#     user_input = state["input"]
#     logging.debug(f"[NODE] agent_node received input: {user_input}")
#     response = llm_with_tools.invoke(        f"You are a helpful assistant. For the question: '{user_input}', decide **if you should call the add_numbers tool**. "
#         "If yes, output something like: TOOL_CALL add_numbers with a=<value> b=<value>. "
#         "If no, simply answer the question."
# )
#     logging.debug(f"[LLM] got response: {response}")
#     # If response has tool_calls attribute:
#     if hasattr(response, "tool_calls"):
#         logging.debug(f"[LLM] tool_calls: {response.tool_calls}")

#     if hasattr(response, "tool_calls") and response.tool_calls:
#         tool_call = response.tool_calls[0]
#         name = tool_call["name"]
#         args = tool_call["args"]
#         # Then execute the tool: e.g. add_numbers(**args)
#     else:
#         # Use response.content directly

#         state["output"] = response.content
#     return state

class Agent_state(TypedDict):
    input:str
    output:str

# Step 4: Create the graph
graph = StateGraph(Agent_state)

# Add nodes
graph.add_node("agent", agent_node)

# Define flow
graph.add_edge("agent", END)
graph.set_entry_point("agent")

# Step 5: Compile the graph into a runnable object
app = graph.compile()

# Step 6: Run the agent
if __name__ == "__main__":
    result = app.invoke({"input": "how are you?"})
    print("response",result["output"])
