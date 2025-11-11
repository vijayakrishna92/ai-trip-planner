from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from langchain_openai import ChatOpenAI

class BudgetState(TypedDict):
    items: List[dict]  # List of {name, cost}
    plan: str
    total_budget: float
    breakdown: List[str]

def planner_agent(state: BudgetState):
    """Plans budget allocation"""
    model = ChatOpenAI(model="gpt-4o")
    items_str = ", ".join([f"{item['name']}: ${item['cost']}" for item in state["items"]])
    
    response = model.invoke(f"Create a budget plan for: {items_str}")
    return {"plan": response.content}

def budget_calculator(state: BudgetState):
    """Calculates total and breakdown"""
    total = sum(item["cost"] for item in state["items"])
    breakdown = [f"{item['name']}: ${item['cost']}" for item in state["items"]]
    
    return {
        "total_budget": total,
        "breakdown": breakdown
    }

# Build graph
graph = (StateGraph(BudgetState)
    .add_node("planner", planner_agent)
    .add_node("calculator", budget_calculator)
    .add_edge(START, "planner")
    .add_edge("planner", "calculator")
    .add_edge("calculator", END)
    .compile())

# Process multiple inputs interactively
inputs = [
    {"items": [{"name": "laptop", "cost": 1200}, {"name": "mouse", "cost": 50}]},
    {"items": [{"name": "desk", "cost": 300}, {"name": "chair", "cost": 200}]}
]

for i, input_data in enumerate(inputs, 1):
    print(f"\n=== Budget {i} ===")
    result = graph.invoke(input_data)
    print(f"Plan: {result['plan']}")
    print(f"Total: ${result['total_budget']}")
    print(f"Breakdown: {result['breakdown']}")