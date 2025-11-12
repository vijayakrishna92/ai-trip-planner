from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_ollama import ChatOllama
from typing import TypedDict

llm = ChatOllama(model="llama3-groq-tool-use:8b")

class Agent_state(TypedDict):
    input:str
    output:str
    memory: list

def user_interact_agent(state:dict):
    """This node takes input from the user and trnsfers task to respective sub agents"""
    user_input = state["input"]
    state["memory"].append(f"User: {user_input}")

    # Ask sub-agent for help (you could add logic to pick others)
    return {"memory": state["memory"], "next": "chat_agent"}
    
def chat_agent(state: dict):
    conversation = "\n".join(state["memory"])
    response = llm.invoke(f"Continue this helpful chat:\n{conversation}")
    state["memory"].append(f"ChatAgent: {response.content}")
    # Send back to main agent for review
    return {"memory": state["memory"], "next": "user_interact_agent"}

agent_builder = StateGraph(Agent_state)
agent_builder.add_node("user_interactor", user_interact_agent)
agent_builder.add_node("chat_agent", chat_agent)
agent_builder.add_edge("user_interactor", "chat_agent")
agent_builder.add_edge("chat_agent", "user_interactor")
agent_builder.set_entry_point("user_interactor")
app = agent_builder.compile()

if __name__ == "__main__":
    state = {"input": "What do you think about space travel?", "output": "", "memory": []}
    result = app.invoke(state)
    print("\n".join(result["memory"]))