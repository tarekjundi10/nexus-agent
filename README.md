# \# Nexus Agent

# 

# Autonomous AI research agent that searches the web, analyzes findings, and delivers structured reports in real time.

# 

# \*\*Live Demo:\*\* https://nexus-agent-26y9.onrender.com

# 

# \## What it does

# 

# Give Nexus a research goal and it autonomously plans search queries, searches the web across multiple sources, synthesizes findings, reflects on report quality, and delivers a structured professional report — all visible in real time through a clean UI.

# 

# \## Features

# 

# \- Live agent thinking feed — watch every step as it happens

# \- Structured reports with Executive Summary, Key Findings, Detailed Analysis, Sources

# \- Fullscreen report mode

# \- Light and dark mode

# \- Download report as Markdown

# \- Enter key to submit

# 

# \## Tech Stack

# 

# Python · LangGraph · GPT-4o · Tavily Search · FastAPI · Render

# 

# \## How to Run Locally

# 

# &#x20;   git clone https://github.com/tarekjundi10/nexus-agent.git

# &#x20;   cd nexus-agent

# &#x20;   pip install -r requirements.txt

# 

# Create a `.env` file:

# 

# &#x20;   OPENAI\_API\_KEY=your-openai-key

# &#x20;   TAVILY\_API\_KEY=your-tavily-key

# 

# Then run:

# 

# &#x20;   uvicorn app.main:app --reload

# 

# Open http://127.0.0.1:8000

# 

# \## Architecture

# 

# The agent is built as a LangGraph state machine with four nodes: plan, search, analyze, and reflect. After drafting a report, the agent reflects on whether the goal is fully addressed and loops back to search if needed, up to a maximum of two iterations.

# 

# \## API Endpoints

# 

# \- `POST /research` — start a research session

# \- `GET /status/{session\_id}` — get live agent steps

# \- `GET /report/{session\_id}` — get the final report

