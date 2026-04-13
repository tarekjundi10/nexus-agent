import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Nexus Agent",
    page_icon="../assets/favicon.png",
    layout="wide"
)

st.title("Nexus Agent")
st.markdown("An autonomous AI research agent that searches the web, analyzes findings, and delivers structured reports.")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Research Goal")
    goal = st.text_area(
        "Enter your research goal",
        placeholder="e.g. What are the latest AI trends in healthcare in 2025?",
        height=120
    )

    run = st.button("Run Research", use_container_width=True, type="primary")

    st.divider()
    st.markdown("#### How it works")
    st.markdown("""
1. Enter a research goal
2. The agent plans search queries
3. Searches the web for sources
4. Analyzes and synthesizes findings
5. Delivers a structured report
""")

with col2:
    if run and goal.strip():
        tab1, tab2 = st.tabs(["Agent Thinking", "Final Report"])

        with tab1:
            st.subheader("Agent Thinking")
            status_box = st.empty()
            steps_box = st.empty()

            # Start research
            response = requests.post(f"{API_URL}/research", json={"goal": goal})
            session_id = response.json()["session_id"]

            # Poll for updates
            while True:
                status_response = requests.get(f"{API_URL}/status/{session_id}")
                data = status_response.json()
                status = data["status"]
                steps = data["steps"]

                status_box.markdown(f"**Status:** `{status}`")

                if steps:
                    steps_text = "\n".join([f"- {s}" for s in steps])
                    steps_box.markdown(steps_text)

                if status in ["complete", "error"]:
                    break

                time.sleep(2)

            if status == "error":
                st.error(f"Error: {data.get('error', 'Unknown error')}")

        with tab2:
            if status == "complete":
                report_response = requests.get(f"{API_URL}/report/{session_id}")
                report = report_response.json().get("report", "")

                st.subheader("Research Report")
                st.markdown(report)

                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        label="Download as Markdown",
                        data=report,
                        file_name="nexus_report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

    elif run and not goal.strip():
        with col2:
            st.warning("Please enter a research goal before running.")

    else:
        with col2:
            st.info("Enter a research goal on the left and click Run Research to begin.")

st.divider()
st.caption("Nexus Agent | Powered by GPT-4o and Tavily | Built with LangGraph and FastAPI")
