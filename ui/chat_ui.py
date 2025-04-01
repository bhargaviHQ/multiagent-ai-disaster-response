import streamlit as st
from src.simulation import run_disaster_simulation  # Only import the function
import threading
import time
import random

# Define bright colors for each agent
AGENT_COLORS = {
    "Controller": "#FF4500",  # Orange Red
    "Routes-1": "#00CED1",    # Dark Turquoise
    "Drone-1": "#FFD700",     # Gold
    "Drone-2": "#FFA500",     # Orange
    "Assess-1": "#32CD32",    # Lime Green
    "Rescue-1": "#FF69B4",    # Hot Pink
    "Supplies-1": "#1E90FF",  # Dodger Blue
    "Supplies-2": "#4169E1",  # Royal Blue
    "Medical-1": "#ADFF2F",   # Green Yellow
    "System": "#808080"       # Gray
}

def run_simulation_in_background(chat_log, agent_status, flowchart):
    print("Starting simulation in background thread")
    run_disaster_simulation(steps=3, ui_mode=True, chat_log=chat_log, agent_status=agent_status, flowchart=flowchart)

def draw_flowchart(flowchart):
    if not flowchart:
        return "<p>No actions yet.</p>"
    
    html = """
    <style>
        .flowchart-container { display: flex; flex-wrap: wrap; gap: 20px; align-items: center; }
        .agent-box { padding: 10px; border-radius: 5px; text-align: center; min-width: 120px; }
        .arrow { margin: 0 10px; font-size: 20px; }
    </style>
    <div class='flowchart-container'>
    """
    for i, (from_agent, to_agent, summary) in enumerate(flowchart):
        from_color = AGENT_COLORS.get(from_agent, "#FFFFFF")
        to_color = AGENT_COLORS.get(to_agent, "#FFFFFF")
        active = st.session_state.agent_status[from_agent]["active"]
        from_style = f"background-color: {from_color}; color: black; opacity: {1.0 if active else 0.5};"
        html += f"<div class='agent-box' style='{from_style}'>{from_agent}<br><small>{summary}</small></div>"
        if i < len(flowchart) - 1 or to_agent != "Controller":
            html += "<span class='arrow'>→</span>"
    html += "</div>"
    return html

def display_chat():
    st.title("Disaster Response Mission")
    
    # Initialize session state and shared data
    if "simulation_running" not in st.session_state:
        st.session_state.simulation_running = False
    if "simulation_started" not in st.session_state:
        st.session_state.simulation_started = False
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []
        st.session_state.agent_status = {agent: {"active": False, "message": ""} for agent in AGENT_COLORS.keys()}
        st.session_state.flowchart = []

    # Use session state variables
    chat_log = st.session_state.chat_log
    agent_status = st.session_state.agent_status
    flowchart = st.session_state.flowchart

    # Start simulation button
    if st.button("Start Simulation") and not st.session_state.simulation_started:
        st.session_state.simulation_started = True
        st.session_state.simulation_running = True
        thread = threading.Thread(target=run_simulation_in_background, args=(chat_log, agent_status, flowchart))
        thread.start()

    # Layout with columns
    col1, col2 = st.columns([1, 3])  # Left sidebar (1/4), Main flowchart (3/4)

    # Left Sidebar: Active Agents
    with col1:
        st.header("Active Agents")
        if not agent_status:
            st.write("No agents initialized yet.")
        else:
            active_found = False
            for agent, status in agent_status.items():
                if status["active"]:
                    st.markdown(f"<span style='color:{AGENT_COLORS.get(agent, '#FFFFFF')}'>{agent}</span>", unsafe_allow_html=True)
                    active_found = True
            if not active_found:
                st.write("No agents currently active.")

    # Main Screen: Flowchart
    with col2:
        st.header("Mission Flowchart")
        st.markdown(draw_flowchart(flowchart), unsafe_allow_html=True)
        st.write(f"Simulation Running: {st.session_state.simulation_running}")

    # Right Toggle Chat
    with st.expander("Chat Log", expanded=False):
        if not chat_log:
            st.write("No messages yet.")
        else:
            for entry in chat_log:
                sender = entry["sender"]
                message = entry["message"]
                color = AGENT_COLORS.get(sender, "#FFFFFF")
                st.markdown(
                    f"""
                    <div style='background-color: {color}; padding: 10px; border-radius: 10px; margin: 5px; color: black;'>
                        <b>{sender}:</b> {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Auto-refresh every 5 seconds while running
    if st.session_state.simulation_running:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    display_chat()