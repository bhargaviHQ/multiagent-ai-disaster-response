import streamlit as st
import streamlit.components.v1 as components
from src.simulation import run_disaster_simulation
import threading
import time
import queue
import csv
from datetime import datetime

AGENT_COLORS = {
    "Controller": "#FFB6A3", "Routes-1": "#A3E8EB", "Drone-1": "#FFEBA3", "Drone-2": "#FFDAA3",
    "Assess-1": "#B3E8B3", "Rescue-1": "#FFB6D6", "Supplies-1": "#B6D6FF", "Supplies-2": "#B6C5EB",
    "Medical-1": "#D6FFB6", "System": "#CCCCCC"
}

# Use a queue to communicate between threads
result_queue = queue.Queue()

def run_simulation_in_background(chat_log, agent_status, flowchart):
    result, disaster_type = run_disaster_simulation(steps=3, ui_mode=True, chat_log=chat_log, agent_status=agent_status, flowchart=flowchart)
    result_queue.put((result, disaster_type))

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
    st.set_page_config(page_title="Response Monitor", layout="wide")
    st.title("Autonomous Rapid Response Monitor")

    # Initialize session state
    if "simulation_running" not in st.session_state:
        st.session_state.simulation_running = False
        st.session_state.chat_log = []
        st.session_state.agent_status = {agent: {"active": False, "message": "", "battery": 100, "task": "", "completed": False} for agent in AGENT_COLORS.keys()}
        st.session_state.flowchart = []
        st.session_state.simulation_result = ""
        st.session_state.disaster_type = "Unknown"
        st.session_state.button_clicked = False

    # Local references to session state
    chat_log = st.session_state.chat_log
    agent_status = st.session_state.agent_status
    flowchart = st.session_state.flowchart

    # Start button with full reset logic
    if st.button("🚀 Start Mission", key="start", help="Click here to start disaster simulation!") and not st.session_state.simulation_running:
        # Reset all previous run's data to clear the UI
        st.session_state.chat_log = []
        st.session_state.agent_status = {agent: {"active": False, "message": "", "battery": 100, "task": "", "completed": False} for agent in AGENT_COLORS.keys()}
        st.session_state.flowchart = []
        st.session_state.simulation_result = ""
        st.session_state.disaster_type = "Unknown"
        
        # Update local references after reset
        chat_log = st.session_state.chat_log
        agent_status = st.session_state.agent_status
        flowchart = st.session_state.flowchart

        # Start the simulation
        st.session_state.simulation_running = True
        thread = threading.Thread(target=run_simulation_in_background, args=(chat_log, agent_status, flowchart))
        thread.start()

    # Check if the simulation has completed
    try:
        result, disaster_type = result_queue.get_nowait()
        st.session_state.simulation_result = result
        st.session_state.disaster_type = disaster_type
        st.session_state.simulation_running = False  # Reset the flag
        # Append to knowledge base after simulation completes
        append_to_knowledge_base(chat_log, disaster_type)
    except queue.Empty:
        pass

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
            st.markdown(f"<span style='color:{color}; background-color:#2d2d2d; padding: 2px 6px; border-radius: 3px'>{agent}</span>: {active} | Battery: {battery}% | Task: {task} | Done: {completed}", unsafe_allow_html=True)

    with col2:
        st.subheader("Mission Flow")
        flowchart_html = draw_flowchart(flowchart)
        components.html(flowchart_html, height=300, scrolling=True)
        if st.session_state.simulation_result:
            st.success(st.session_state.simulation_result)

    with col3:
        disaster_alert = None
        simulation_complete = False
        resolved_agents = []
        for entry in chat_log:
            if entry["sender"] == "System":
                if "Simulation complete" in entry["message"]:
                    simulation_complete = True
                    resolved_agents = ["Medical Team", "Fire Department"]  # Parse this if needed
                elif "Disaster Type" in entry["message"]:
                    disaster_alert = entry["message"]

        if disaster_alert:
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #FFE082, #FFD54F); padding: 15px; border-radius: 10px; border-left: 5px solid #FFA000; margin-bottom: 20px; animation: pulse 1.5s infinite;'>
                    <h3 style='color: #5D4037; margin: 0; padding: 0; font-weight: 800;'>⚠️ DISASTER ALERT</h3>
                    <p style='color: #5D4037; margin: 8px 0 0 0; font-size: 18px; font-weight: 600;'>{disaster_alert}</p>
                </div>
                <style>
                    @keyframes pulse {{
                        0% {{ box-shadow: 0 0 0 0 rgba(255,160,0,0.7); transform: scale(1); }}
                        50% {{ box-shadow: 0 0 0 15px rgba(255,160,0,0.2); transform: scale(1.01); }}
                        100% {{ box-shadow: 0 0 0 0 rgba(255,160,0,0); transform: scale(1); }}
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )

        if simulation_complete:
            agents_list = ", ".join(resolved_agents) if resolved_agents else "multiple response teams"
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #C8E6C9, #A5D6A7); padding: 20px; border-radius: 10px; border-left: 5px solid #388E3C; margin-bottom: 20px; animation: success-pulse 2s infinite;'>
                    <h3 style='color: #1B5E20; margin: 0; padding: 0; font-weight: 800;'>✅ DISASTER MITIGATED</h3>
                    <p style='color: #1B5E20; margin: 10px 0 5px 0; font-size: 18px; font-weight: 600;'>The disaster scenario has been resolved.</p>
                    <p style='color: #1B5E20; margin: 5px 0 0 0; font-size: 16px;'>{disaster_alert if disaster_alert else "N/A"}</p>
                </div>
                <style>
                    @keyframes success-pulse {{
                        0% {{ box-shadow: 0 0 0 0 rgba(56, 142, 60, 0.4); transform: scale(1); }}
                        70% {{ box-shadow: 0 0 0 12px rgba(56, 142, 60, 0); transform: scale(1.005); }}
                        100% {{ box-shadow: 0 0 0 0 rgba(56, 142, 60, 0); transform: scale(1); }}
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )

        with st.expander("Detailed Chat Log", expanded=True):
            for entry in chat_log:
                sender = entry["sender"]
                message = entry["message"]
                color = AGENT_COLORS.get(sender, "#FFFFFF")
                st.markdown(f"<div style='background-color: {color}; padding: 8px; border-radius: 5px; margin: 5px; color: black;'><b>{sender}:</b> {message}</div>", unsafe_allow_html=True)

    # Auto-refresh while simulation is running
    if st.session_state.simulation_running:
        time.sleep(1)
        st.rerun()

def append_to_knowledge_base(chat_log, disaster_type):
    """Append disaster data to a CSV knowledge base."""
    # Extract data from chat log
    disaster_info = None
    routes_optimized = "N/A"
    for entry in chat_log:
        if entry["sender"] == "System" and "Disaster Type" in entry["message"]:
            disaster_info = entry["message"]  # e.g., "Disaster Type: earthquake | Affected Areas: 8"
        if entry["sender"] == "Routes-1":
            routes_optimized = entry["message"]  # e.g., response about cleared routes

    if disaster_info:
        # Parse disaster type and affected areas
        parts = disaster_info.split(" | ")
        disaster_type = parts[0].replace("Disaster Type: ", "").strip()
        affected_areas = parts[1].replace("Affected Areas: ", "").strip()

        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Define CSV file and headers
        csv_file = "disaster_knowledge_base.csv"
        headers = ["Timestamp", "Disaster Type", "Affected Areas"]

        # Append data to CSV
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header if file is new/empty
            if f.tell() == 0:
                writer.writerow(headers)
            writer.writerow([timestamp, disaster_type, affected_areas])
if __name__ == "__main__":
    display_chat()