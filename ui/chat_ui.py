import streamlit as st
import streamlit.components.v1 as components
from src.simulation import run_disaster_simulation
import threading
import time

AGENT_COLORS = {
    "Controller": "#FF4500", "Routes-1": "#00CED1", "Drone-1": "#FFD700", "Drone-2": "#FFA500",
    "Assess-1": "#32CD32", "Rescue-1": "#FF69B4", "Supplies-1": "#1E90FF", "Supplies-2": "#4169E1",
    "Medical-1": "#ADFF2F", "System": "#808080"
}

def run_simulation_in_background(chat_log, agent_status, flowchart):
    result, disaster_type = run_disaster_simulation(steps=3, ui_mode=True, chat_log=chat_log, agent_status=agent_status, flowchart=flowchart)
    st.session_state.simulation_result = result
    st.session_state.disaster_type = disaster_type

def draw_flowchart(flowchart):
    if not flowchart:
        return "<p>No actions yet.</p>"

    html = """
    <style>
        .flowchart { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            padding: 15px; 
            background: #1a1a1a; 
            border-radius: 10px; 
            border: 1px solid #444; 
            align-items: center; 
        }
        .agent-box { 
            padding: 10px; 
            border-radius: 8px; 
            text-align: center; 
            font-size: 14px; 
            position: relative; 
            min-width: 150px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3); 
        }
        .agent-box.completed { 
            border: 2px solid #00FF00; 
        }
        .agent-box.incomplete { 
            border: 2px solid #FF0000; 
        }
        .arrow { 
            margin: 0 5px; 
            font-size: 16px; 
            color: #888; 
        }
        .task-text { 
            font-size: 12px; 
            margin-top: 5px; 
            word-wrap: break-word; 
        }
    </style>
    <div class='flowchart'>
    """
    for i, (from_agent, to_agent, action, completed) in enumerate(flowchart):
        color = AGENT_COLORS.get(from_agent, "#FFFFFF")
        status_class = "completed" if completed else "incomplete"
        html += f"""
        <div class='agent-box {status_class}' style='background-color: {color}; color: black;'>
            <strong>{from_agent}</strong>
            <div class='task-text'>{action}</div>
        </div>
        """
        if i < len(flowchart) - 1:
            html += "<span class='arrow'>→</span>"
    html += "</div>"
    return html

def display_chat():
    st.set_page_config(page_title="Disaster Response", layout="wide")
    st.title("Disaster Response Dashboard")

    if "simulation_running" not in st.session_state:
        st.session_state.simulation_running = False
        st.session_state.chat_log = []
        st.session_state.agent_status = {agent: {"active": False, "message": "", "battery": 100, "task": "", "completed": False} for agent in AGENT_COLORS.keys()}
        st.session_state.flowchart = []
        st.session_state.simulation_result = ""
        st.session_state.disaster_type = "Unknown"

    chat_log = st.session_state.chat_log
    agent_status = st.session_state.agent_status
    flowchart = st.session_state.flowchart

    # Start button
    if st.button("Start Mission", key="start") and not st.session_state.simulation_running:
        st.session_state.simulation_running = True
        thread = threading.Thread(target=run_simulation_in_background, args=(chat_log, agent_status, flowchart))
        thread.start()

    # Three-column layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.subheader("Agent Status")
        for agent, status in agent_status.items():
            color = AGENT_COLORS.get(agent, "#FFFFFF")
            battery = status["battery"]
            active = "Active" if status["active"] else "Inactive"
            task = status["task"] if status["task"] else "No task"
            completed = "✔" if status["completed"] else "✘"
            st.markdown(f"<span style='color:{color}'>{agent}</span>: {active} | Battery: {battery}% | Task: {task} | Done: {completed}", unsafe_allow_html=True)

    with col2:
        #st.subheader("Mission Flow")
        #st.markdown(f"<p style='color: #888; font-size: 16px;'>Disaster: {st.session_state.disaster_type}</p>", unsafe_allow_html=True)
        st.subheader("Mission Flow")
        st.markdown(f"<p style='color: #888; font-size: 16px;'>Disaster: {st.session_state.disaster_type}</p>", unsafe_allow_html=True)
        # Use st.components.v1.html to render the flowchart
        flowchart_html = draw_flowchart(flowchart)
        components.html(flowchart_html, height=300, scrolling=True)
        if st.session_state.simulation_result:
            st.success(st.session_state.simulation_result)

    with col3:
        with st.expander("Detailed Chat Log", expanded=False):
            for entry in chat_log:
                sender = entry["sender"]
                message = entry["message"]
                color = AGENT_COLORS.get(sender, "#FFFFFF")
                st.markdown(f"<div style='background-color: {color}; padding: 8px; border-radius: 5px; margin: 5px; color: black;'><b>{sender}:</b> {message}</div>", unsafe_allow_html=True)

    if st.session_state.simulation_running:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    display_chat()