from src.agents import get_agents  # Import the function, not the variable
from src.environment import DisasterEnvironment
import time
import random  

def run_disaster_simulation(steps=3, ui_mode=False, chat_log=None, agent_status=None, flowchart=None):
    # Initialize if not provided
    if chat_log is None:
        chat_log = []
    if agent_status is None:
        agents = get_agents()  # Call the function here
        agent_status = {agent.name: {"active": False, "message": ""} for agent in agents.values()}
    else:
        agents = get_agents()  # Still need agents for the simulation
    if flowchart is None:
        flowchart = []

    env = DisasterEnvironment()
    #initial_message = f"Disaster Type: {env.disaster_type}"
    initial_message = (
            f"Simulation {simulation_id} - Disaster Type: {env.disaster_type}\n"
            f"Agents Deployed: {len(agents)}\n{agent_details}"
        )

    if ui_mode:
        print("UI Mode: Starting simulation")
        chat_log.append({"sender": "System", "message": initial_message})
    else:
        print(f"\n=== DISASTER SIMULATION STARTED ===\n{initial_message}\n")

    agent_status["Controller"]["active"] = True

    for step in range(steps):
        if ui_mode:
            chat_log.append({"sender": "System", "message": f"Step {step + 1}"})
            print(f"UI Mode: Starting Step {step + 1}")
        else:
            print(f"\n=== STEP {step + 1} ===")
        
        env.update_environment()
        env_data = env.get_report()

        # Controller initiates
        agent_status["Controller"]["active"] = True
        controller_task = f"Coordinate response for {env.disaster_type}. Affected areas: {env_data['affected_areas']}. Victims: {env_data['victim_locations']}. Supplies needed: {env_data['supply_needs']}."
        controller_response = agents["controller"].perform_task(controller_task)
        agent_status["Controller"]["message"] = controller_response
        summary = "Initiated response"
        if ui_mode:
            print(f"Appending to chat_log: {controller_response}")
            chat_log.append({"sender": "Controller", "message": controller_response})
        else:
            print(f"{agents['controller'].name}: {controller_response}")
        time.sleep(5)

        # Routes
        agent_status["Routes-1"]["active"] = True
        agents["controller"].send_message(agents["routes"], f"Clear routes in affected areas: {env_data['blocked_routes']}.")
        flowchart.append(("Controller", "Routes-1", "Clear routes"))
        routes_task = f"Assess and clear blocked routes: {env_data['blocked_routes']} due to {env.disaster_type}."
        routes_response = agents["routes"].perform_task(routes_task)
        agent_status["Routes-1"]["message"] = routes_response
        summary = "Routes cleared"
        agents["routes"].send_message(agents["controller"], f"Routes update: {routes_response}")
        if ui_mode:
            print(f"Appending to chat_log: {routes_response}")
            chat_log.append({"sender": "Routes-1", "message": routes_response})
            flowchart.append(("Routes-1", "Controller", summary))
        else:
            print(f"Routes update: {routes_response}")
        agent_status["Routes-1"]["active"] = False
        time.sleep(20)

        # Drone
        if agents["drone"].status == "inactive":
            agents["drone"] = agents["drone"].activate_backup() or agents["drone"]
        agent_status[agents["drone"].name]["active"] = True
        agents["controller"].send_message(agents["drone"], f"Survey for victims and hazards in {env_data['affected_areas']}.")
        flowchart.append(("Controller", agents["drone"].name, "Survey area"))
        drone_task = f"Conduct aerial survey over {env_data['affected_areas']} for {env.disaster_type} impact."
        drone_response = agents["drone"].perform_task(drone_task)
        agent_status[agents["drone"].name]["message"] = drone_response
        summary = "Victims detected" if "victim" in drone_response.lower() else "Area surveyed"
        agents["drone"].send_message(agents["controller"], f"Survey report: {drone_response}")
        if ui_mode:
            print(f"Appending to chat_log: {drone_response}")
            chat_log.append({"sender": agents["drone"].name, "message": drone_response})
            flowchart.append((agents["drone"].name, "Controller", summary))
        else:
            print(f"Survey report: {drone_response}")
        agent_status[agents["drone"].name]["active"] = False
        time.sleep(20)

        # Assess
        agent_status["Assess-1"]["active"] = True
        agents["controller"].send_message(agents["assess"], f"Evaluate damage in {env_data['affected_areas']}.")
        flowchart.append(("Controller", "Assess-1", "Assess damage"))
        assess_task = f"Assess structural integrity and hazards in {env_data['affected_areas']} due to {env.disaster_type}."
        assess_response = agents["assess"].perform_task(assess_task)
        agent_status["Assess-1"]["message"] = assess_response
        summary = "Damage assessed"
        agents["assess"].send_message(agents["controller"], f"Damage report: {assess_response}")
        if ui_mode:
            print(f"Appending to chat_log: {assess_response}")
            chat_log.append({"sender": "Assess-1", "message": assess_response})
            flowchart.append(("Assess-1", "Controller", summary))
        else:
            print(f"Damage report: {assess_response}")
        agent_status["Assess-1"]["active"] = False
        time.sleep(20)

        # Rescue
        if env_data["victim_locations"]:
            agent_status["Rescue-1"]["active"] = True
            agents["controller"].send_message(agents["rescue"], f"Extract victims from {env_data['victim_locations']}.")
            flowchart.append(("Controller", "Rescue-1", "Rescue victims"))
            rescue_task = f"Rescue operations at {env_data['victim_locations']} amidst {env.disaster_type} conditions."
            rescue_response = agents["rescue"].perform_task(rescue_task)
            agents["rescue"].update_location(random.choice(env_data["victim_locations"]))
            agent_status["Rescue-1"]["message"] = rescue_response
            summary = "Victims rescued"
            agents["rescue"].send_message(agents["controller"], f"Rescue update: {rescue_response}")
            if ui_mode:
                print(f"Appending to chat_log: {rescue_response}")
                chat_log.append({"sender": "Rescue-1", "message": rescue_response})
                flowchart.append(("Rescue-1", "Controller", summary))
            else:
                print(f"Rescue update: {rescue_response}")
            env.completed_tasks["rescued"].extend(env_data["victim_locations"])
            agent_status["Rescue-1"]["active"] = False
            time.sleep(20)

        # Supplies
        if agents["supplies"].status == "inactive":
            agents["supplies"] = agents["supplies"].activate_backup() or agents["supplies"]
        if env_data["supply_needs"]:
            agent_status[agents["supplies"].name]["active"] = True
            agents["controller"].send_message(agents["supplies"], f"Deliver to {env_data['supply_needs']} via cleared routes.")
            flowchart.append(("Controller", agents["supplies"].name, "Deliver supplies"))
            supplies_task = f"Transport supplies to {env_data['supply_needs']} under {env.disaster_type} conditions."
            supplies_response = agents["supplies"].perform_task(supplies_task)
            agents["supplies"].update_location((env_data['supply_needs'][0][0], env_data['supply_needs'][0][1]) if env_data['supply_needs'] else (0, 0))
            agent_status[agents["supplies"].name]["message"] = supplies_response
            summary = "Supplies delivered"
            agents["supplies"].send_message(agents["controller"], f"Supply update: {supplies_response}")
            if ui_mode:
                print(f"Appending to chat_log: {supplies_response}")
                chat_log.append({"sender": agents["supplies"].name, "message": supplies_response})
                flowchart.append((agents["supplies"].name, "Controller", summary))
            else:
                print(f"Supply update: {supplies_response}")
            env.completed_tasks["supplied"].extend(env_data["supply_needs"])
            agent_status[agents["supplies"].name]["active"] = False
            time.sleep(20)

        # Medical
        if env_data["victim_locations"]:
            agent_status["Medical-1"]["active"] = True
            agents["controller"].send_message(agents["medical"], f"Provide medical aid at {env_data['victim_locations']}.")
            flowchart.append(("Controller", "Medical-1", "Provide aid"))
            medical_task = f"Treat victims at {env_data['victim_locations']} affected by {env.disaster_type}."
            medical_response = agents["medical"].perform_task(medical_task)
            agents["medical"].update_location(random.choice(env_data["victim_locations"]))
            agent_status["Medical-1"]["message"] = medical_response
            summary = "Victims treated"
            agents["medical"].send_message(agents["controller"], f"Medical update: {medical_response}")
            if ui_mode:
                print(f"Appending to chat_log: {medical_response}")
                chat_log.append({"sender": "Medical-1", "message": medical_response})
                flowchart.append(("Medical-1", "Controller", summary))
            else:
                print(f"Medical update: {medical_response}")
            agent_status["Medical-1"]["active"] = False
            time.sleep(20)

        if not ui_mode:
            print("\nAgent Status:")
            for agent in agents.values():
                print(agent.report_status())
        
        time.sleep(10)

    if not ui_mode:
        print("\n=== SIMULATION COMPLETE ===")