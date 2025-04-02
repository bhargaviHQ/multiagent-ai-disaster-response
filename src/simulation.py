from src.agents import get_agents
from src.environment import DisasterEnvironment
import time
import random

def run_disaster_simulation(steps=3, ui_mode=False, chat_log=None, agent_status=None, flowchart=None):
    if chat_log is None:
        chat_log = []
    if agent_status is None:
        agents = get_agents()
        agent_status = {agent.name: {"active": False, "message": "", "battery": 100, "task": "", "completed": False} for agent in agents.values()}
    else:
        agents = get_agents()
    if flowchart is None:
        flowchart = []

    env = DisasterEnvironment()
    disaster_type = env.disaster_type
    initial_message = f"Disaster Type: {env.disaster_type} | Affected Areas: {len(env.affected_areas)}"
    chat_log.append({"sender": "System", "message": initial_message})

    for step in range(steps):
        chat_log.append({"sender": "System", "message": f"Step {step + 1} starting..."})
        env.update_environment()
        env_data = env.get_report()

        # Random device failure
        for agent in agents.values():
            if random.random() < 0.1 and agent.status == "active":  # 10% chance of failure
                agent.status = "inactive"
                agent_status[agent.name]["battery"] = 0
                chat_log.append({"sender": "System", "message": f"{agent.name} failed unexpectedly!"})

        # Controller
        agent_status["Controller"]["active"] = True
        agent_status["Controller"]["task"] = "Coordinate response"
        controller_task = f"Coordinate for {env.disaster_type}. Areas: {env_data['affected_areas']}"
        controller_response = agents["controller"].perform_task(controller_task)
        agent_status["Controller"]["message"] = controller_response
        agent_status["Controller"]["completed"] = True
        chat_log.append({"sender": "Controller", "message": controller_response})
        flowchart.append(("Controller", "All", "Coordinate response", True))

        # Routes
        agent_status["Routes-1"]["active"] = True
        agent_status["Routes-1"]["task"] = f"Clear routes: {env_data['blocked_routes']}"
        routes_task = f"Clear routes: {env_data['blocked_routes']}"
        routes_response = agents["routes"].perform_task(routes_task)
        agent_status["Routes-1"]["message"] = routes_response
        agent_status["Routes-1"]["completed"] = True
        chat_log.append({"sender": "Routes-1", "message": routes_response})
        flowchart.append(("Routes-1", "Controller", f"Clear routes: {env_data['blocked_routes']}", True))  # Fixed: "Routes-1" as from_agent

        # Drone with random coordinates
        if agents["drone"].status == "inactive":
            agents["drone"] = agents["drone"].activate_backup() or agents["drone"]
        agent_status[agents["drone"].name]["active"] = True
        random_area = random.choice(env_data["affected_areas"]) if env_data["affected_areas"] else (random.randint(0, 100), random.randint(0, 100))
        agent_status[agents["drone"].name]["task"] = f"Survey {random_area}"
        drone_task = f"Survey {random_area}"
        drone_response = agents["drone"].perform_task(drone_task)
        agent_status[agents["drone"].name]["message"] = drone_response
        agent_status[agents["drone"].name]["completed"] = True
        chat_log.append({"sender": agents["drone"].name, "message": drone_response})
        flowchart.append((agents["drone"].name, "Controller", f"Survey {random_area}", True))  # Fixed: Drone name as from_agent

        # Assess
        agent_status["Assess-1"]["active"] = True
        random_area = random.choice(env_data["affected_areas"]) if env_data["affected_areas"] else (0, 0)
        agent_status["Assess-1"]["task"] = f"Assess {random_area}"
        assess_task = f"Assess {random_area}"
        assess_response = agents["assess"].perform_task(assess_task)
        agent_status["Assess-1"]["message"] = assess_response
        agent_status["Assess-1"]["completed"] = True
        chat_log.append({"sender": "Assess-1", "message": assess_response})
        flowchart.append(("Assess-1", "Controller", f"Assess {random_area}", True))  # Fixed: "Assess-1" as from_agent

        # Rescue
        if env_data["victim_locations"]:
            agent_status["Rescue-1"]["active"] = True
            random_victim = random.choice(env_data["victim_locations"])
            agent_status["Rescue-1"]["task"] = f"Rescue at {random_victim}"
            rescue_task = f"Rescue at {random_victim}"
            rescue_response = agents["rescue"].perform_task(rescue_task)
            agents["rescue"].update_location(random_victim)
            agent_status["Rescue-1"]["message"] = rescue_response
            agent_status["Rescue-1"]["completed"] = True
            chat_log.append({"sender": "Rescue-1", "message": rescue_response})
            flowchart.append(("Rescue-1", "Controller", f"Rescue at {random_victim}", True))  # Fixed: "Rescue-1" as from_agent
            env.completed_tasks["rescued"].append(random_victim)

        # Supplies
        if agents["supplies"].status == "inactive":
            agents["supplies"] = agents["supplies"].activate_backup() or agents["supplies"]
        if env_data["supply_needs"]:
            agent_status[agents["supplies"].name]["active"] = True
            random_need = random.choice(env_data["supply_needs"])
            agent_status[agents["supplies"].name]["task"] = f"Deliver to {random_need}"
            supplies_task = f"Deliver to {random_need}"
            supplies_response = agents["supplies"].perform_task(supplies_task)
            agents["supplies"].update_location((random_need[0], random_need[1]))
            agent_status[agents["supplies"].name]["message"] = supplies_response
            agent_status[agents["supplies"].name]["completed"] = True
            chat_log.append({"sender": agents["supplies"].name, "message": supplies_response})
            flowchart.append((agents["supplies"].name, "Controller", f"Deliver to {random_need}", True))  # Fixed: Supplies name as from_agent
            env.completed_tasks["supplied"].append(random_need)

        # Medical
        if env_data["victim_locations"]:
            agent_status["Medical-1"]["active"] = True
            random_victim = random.choice(env_data["victim_locations"])
            agent_status["Medical-1"]["task"] = f"Treat at {random_victim}"
            medical_task = f"Treat at {random_victim}"
            medical_response = agents["medical"].perform_task(medical_task)
            agents["medical"].update_location(random_victim)
            agent_status["Medical-1"]["message"] = medical_response
            agent_status["Medical-1"]["completed"] = True
            chat_log.append({"sender": "Medical-1", "message": medical_response})
            flowchart.append(("Medical-1", "Controller", f"Treat at {random_victim}", True))  # Fixed: "Medical-1" as from_agent

        # Update battery levels
        for agent in agents.values():
            if agent.status == "active":
                agent_status[agent.name]["battery"] -= random.randint(5, 15)
                if agent_status[agent.name]["battery"] <= 0:
                    agent.status = "inactive"
                    chat_log.append({"sender": "System", "message": f"{agent.name} battery depleted!"})

        time.sleep(5)

    chat_log.append({"sender": "System", "message": "Simulation complete"})
    return "Simulation completed successfully", disaster_type