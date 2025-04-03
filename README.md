## Overview
This project implements a Multi-Agent System (MAS) to simulate disaster response scenarios like earthquakes, floods, and wildfires. Built with Python and Streamlit, it features autonomous agents such as Controller, Rescue, and Drone. The system uses a Groq cloud with  `Deepseek R1 Distill Llama 70B` model for agent decision-making, dynamically assigning tasks such as victim rescue, supply delivery, damage assessment, and route clearing.

The `DisasterEnvironment` class generates and updates a 100x100 grid with affected areas, blocked routes, and victim locations, while `simulation.py` manages the workflow, including random agent failures (10% chance) and battery depletion. The Streamlit UI visualizes agent statuses, a mission flowchart, and chat logs while logging results to a CSV knowledge base for future use.

## Workflow  

The system operates as a coordinated workflow involving multiple agents and components.  

- Initialization  
    - The `DisasterEnvironment` generates a random disaster scenario (earthquake, flood, or wildfire) with affected areas, blocked routes, victim locations, and supply needs. 
    - Agents are instantiated with specific roles and capabilities via `get_agents()`.  

- Simulation Loop (`run_disaster_simulation`)  
    - The environment updates dynamically (e.g., wildfires spread, floods shift blockages).  
    - Agents perform tasks assigned by the Controller, with a 10% chance of random failure to simulate real-world unpredictability.  
    - Tasks are logged in a chat log, agent statuses are tracked, and a flowchart visualizes the mission flow.  

- Agent Coordination  
    - The Controller assigns tasks based on environmental data.  
    - Agents execute tasks, communicate results, and update their status (e.g., battery levels, location).  

- UI Rendering (`chat_ui.py`)  
    - A Streamlit interface displays agent statuses, mission flow (flowchart), and chat logs in real-time.  
    - The simulation auto-refreshes during execution and saves results to a knowledge base (`disaster_knowledge_base.csv`).  

- Completion  
    - The simulation ends after a set number of steps or when tasks are resolved, displaying a success message.  


## Agent Types & Details  

The agents operate in a hierarchical structure with the Controller as the central hub. 
- **Controller**: Acts as the orchestrator, assigning tasks to all other agents based on the disaster environment’s state. 
- **Other Agents** (Rescue-1, Drone-1, Medical-1, Assess-1, Supplies-1, Routes-1): These are task executors that receive instructions from the Controller and report back their results. They don’t directly communicate with each other; all communication flows through the Controller.
- **Backup Agents** (Drone-2, Supplies-2): These are activated only if their primary counterparts (Drone-1, Supplies-1) fail due to battery depletion or random failure. They inherit the same role and relationship with the Controller.

### Total Agents  
There are a total of 9 agents, with 7 active at initialization and 2 backup agents available if needed.  

- **Active Agents:** 7  
- **Backup Agents:** 2 (*Drone-2* and *Supplies-2*)  

### Agent Specifications

1. **Controller Agent**  
   - Role: Central coordinator; assigns tasks and develops rescue plans.  
   - Capabilities:  
     - Task allocation.  
     - Does not perform physical tasks.  
     - Coordinates the response by assigning tasks to other agents.  
     - Manages agent statuses and workflow.  
   - Name: <mark>Controller</mark>  

2. **Rescue Agent**  
   - Role: Extracts victims from disaster zones and provides first aid.  
   - Capabilities: Victim extraction, first aid.  
   - Name: <mark>Rescue-1</mark>  

3. **Drone Agents**  
   - Role: Surveys hard-to-reach areas and detects victims.  
   - Capabilities: Surveillance, victim detection.  
   - Name: <mark>Drone-1,</mark> <mark>Drone-2</mark>  

4. **Medical Agent**  
   - Role: Treats injured victims and coordinates transport.  
   - Capabilities: Treatment, transport.  
   - Name: <mark>Medical-1</mark>  

5. **Assess Agent**  
   - Role: Analyzes structural damage and detects hazards.  
   - Capabilities: Structural analysis, hazard detection.  
   - Name: <mark>Assess-1</mark>  

6. **Supplies Agents**  
   - Role: Delivers essential supplies (food, water, medical).  
   - Capabilities: Food, water, medical supply delivery.  
   - Name: <mark>Supplies-1,</mark> <mark>Supplies-2</mark>  

7. **Routes Agent**  
   - Role: Plans and clears evacuation routes.  
   - Capabilities: Route planning, barricade management.  
   - Name: <mark>Routes-1</mark>  

 

#### Relationship Summary

- One-to-Many: Controller → All other agents (uni-directional task assignment).  
- Feedback Loop: Agents → Controller (report task completion or status).  
- No Peer-to-Peer: Agents don’t interact directly with each other.  

#### Order of Controller Communication
The Controller communicates with each agent sequentially in this order within each simulation step.
- If an agent is inactive (e.g., due to failure or battery depletion), its task is skipped or delegated to a backup (for Drone-1 and Supplies-1).
- The order reflects a logical progression; planning (Controller), infrastructure (Routes-1), reconnaissance (Drone-1), assessment (Assess-1), and then action (Rescue-1, Supplies-1, Medical-1).

Note: The Controller’s communication order is fixed, but task execution depends on the environment (e.g., Rescue-1 and Medical-1 only act if victims exist).


[View Detailed Controller Communication Sequence with Agent States and Backups](https://github.com/bhargaviHQ/multiagent-ai-disaster-response/blob/main/docs/img/Controller-Sequence-Details.png)

Summary of Controller Communication Order:
![Summary of Controller Communication Order](https://github.com/bhargaviHQ/multiagent-ai-disaster-response/blob/main/docs/img/Controller-Sequence-Summary.png)


```
Controller  
   ├──→ Routes-1       (Step 1: Clear routes)  
   ├──→ Drone-1/2      (Step 2: Survey areas)  
   ├──→ Assess-1       (Step 3: Assess damage)  
   ├──→ Rescue-1       (Step 4: Rescue victims)  
   ├──→ Supplies-1/2   (Step 5: Deliver supplies)  
   └──→ Medical-1      (Step 6: Treat victims)  
```
### Usage

#### Installation
1. Clone the Repository
    ```bash
    git clone https://github.com/bhargaviHQ/multiagent-ai-disaster-response.git
    cd multiagent-ai-disaster-response
    ```

2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Set Up Environment Variables
    - Create a `config/.env` file.
    - Add your Groq API key to the file:
    
        ```text
        GROQ_API_KEY=your_groq_api_key_here
        ```

4. Run the Application
    ```bash
    python app.py
    ```

#### App Instructions
-  Open your browser and go to `http://localhost:8501` to view the Streamlit UI.

- Click **"🚀 Start Mission"** button to begin the simulation.

- Monitor the UI:
    - **Agent Status:** View active agents, progress, battery levels, and tasks.
    - **Mission Flow:** See the flowchart of agent actions.
    - **Chat Log:** Read detailed agent communications and system updates.

- Review the `disaster_knowledge_base.csv` file for the simulation history.

#### Tools Used
- Python 
- Streamlit: Web-based UI for real-time visualization  
- Groq API: Language model for agent decision-making and task responses  
- LangChain: Message handling for LLM interactions (HumanMessage, AIMessage, SystemMessage)  
- Threading: Background simulation execution to keep the UI responsive. 

#### Requirements
- A stable internet connection to access the Groq API.
- A valid Groq API key, available from groq.com.


## Future Enhancements

1. Redesign the Controller to execute agent tasks in parallel using threads/asyncio.
2. Implement direct agent-to-agent communication beyond the Controller (P2P).
3. Add more disaster types (e.g., hurricanes, tsunamis) with unique dynamics.
4. Enhance the UI with interactive controls like pause or step-through simulation.
5. Integrate human-in-the-loop for dynamic decision-making.

**Note:** In the current implementation, Medical-1 depends on prior steps (Routes-1, Drone-1/2, Assess-1, Rescue-1) to ensure victims are reachable and resources are used efficiently. Acting first risks wasting resources on inaccessible areas. The sequence ensures optimal resource allocation, validates victim presence, and avoids chaotic responses by stabilizing the situation before medical intervention. This approach can be changed according to the required priority.

## Repo Overview
```
multiagent-ai-disaster-response
│
├── src/                    # Core logic and agent definitions
│   ├── agents.py           # Defines agent classes and their capabilities
│   ├── environment.py      # Simulates the disaster environment
│   ├── groq_llm.py         # Integrates the Groq API for language modeling
│   ├── simulation.py       # Manages disaster simulation logic
│   └── __init__.py         # Initializes the src module
│
├── ui/                     # User interface components
│   ├── chat_ui.py          # Streamlit based UI with mission flowchart
│   └── __init__.py         # Initializes the ui module
│
├── config/                 # Configuration files
│   ├── .env                # Stores environment variables (GROQ_API_KEY)
│   └── settings.py         # Project settings
│
├── main.py                 # Optional entry point 
├── app.py                  # Launches the Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation (this file)
└── .gitignore              # Specifies files to ignore in Git
```
