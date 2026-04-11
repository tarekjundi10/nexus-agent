import os
import json
from typing import TypedDict, Callable, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.tools import web_search, synthesize_findings
from agent.prompts import SYSTEM_PROMPT, PLAN_PROMPT, REFLECT_PROMPT

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


class AgentState(TypedDict):
    goal: str
    queries: list
    findings: list
    report: str
    steps: list
    reflection: str
    iteration: int
    callback: Any


def add_step(state: AgentState, step: str):
    state["steps"].append(step)
    if state.get("callback"):
        state["callback"](step)


def plan_node(state: AgentState) -> AgentState:
    add_step(state, "Planning research queries...")
    prompt = PLAN_PROMPT.format(goal=state["goal"])
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])
    try:
        queries = json.loads(response.content)
    except Exception:
        queries = [state["goal"]]
    state["queries"] = queries
    add_step(state, f"Generated {len(queries)} search queries.")
    return state


def search_node(state: AgentState) -> AgentState:
    all_findings = []
    for query in state["queries"]:
        add_step(state, f"Searching: {query}")
        results = web_search(query, max_results=3)
        all_findings.extend(results)
    state["findings"] = all_findings
    add_step(state, f"Retrieved {len(all_findings)} sources.")
    return state


def analyze_node(state: AgentState) -> AgentState:
    add_step(state, "Analyzing and synthesizing findings...")
    report = synthesize_findings(state["goal"], state["findings"])
    state["report"] = report
    add_step(state, "Report drafted.")
    return state


def reflect_node(state: AgentState) -> AgentState:
    add_step(state, "Reflecting on report quality...")
    prompt = REFLECT_PROMPT.format(goal=state["goal"], report=state["report"])
    response = llm.invoke([HumanMessage(content=prompt)])
    state["reflection"] = response.content.strip().upper()
    state["iteration"] = state.get("iteration", 0) + 1
    add_step(state, f"Reflection: {state['reflection']}")
    return state


def should_continue(state: AgentState) -> str:
    if state["reflection"] == "YES" or state["iteration"] >= 2:
        return "end"
    return "search"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("reflect", reflect_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "reflect")
    graph.add_conditional_edges(
        "reflect",
        should_continue,
        {"end": END, "search": "search"}
    )
    return graph.compile()