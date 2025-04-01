from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import random
from src.groq_llm import GroqLLM

class DisasterResponseAgent:
    def __init__(self, name, agent_type, capabilities, llm, backups=None):
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.llm = llm
        self.memory = []
        self.status = "active"
        self.location = (0, 0)
        self.battery = 100
        self.data = {}
        self.backups = backups or []

    def receive_message(self, sender, message):
        self.memory.append(AIMessage(content=f"From {sender}: {message}"))
        return f"{self.name} received message from {sender}"

    def send_message(self, recipient, message):
        print(f"{self.name} -> {recipient.name}: {message}")
        return recipient.receive_message(self.name, message)

    def perform_task(self, task):
        if self.status == "inactive":
            return f"{self.name} is inactive, task aborted."
        self.battery -= random.randint(5, 20)
        if self.battery <= 0:
            self.status = "inactive"
            return f"{self.name} battery depleted, going inactive."
        
        messages = [
            SystemMessage(content=f"""You are {self.name}, a {self.agent_type} with capabilities: {', '.join(self.capabilities)}.
            Status: {self.status}, Location: {self.location}, Battery: {self.battery}%.
            Provide detailed, realistic responses for disaster scenarios.""")
        ]
        messages.extend(self.memory[-5:])
        messages.append(HumanMessage(content=task))
        
        response = self.llm(messages)
        self.memory.append(AIMessage(content=response))
        return response

    def update_location(self, new_location):
        self.location = new_location
        return f"{self.name} moved to {new_location}"

    def activate_backup(self):
        if self.backups and self.status == "inactive":
            backup = self.backups.pop(0)
            backup.status = "active"
            print(f"{self.name} activating backup: {backup.name}")
            return backup
        return None

    def report_status(self):
        return f"{self.name} (Type: {self.agent_type}) - Status: {self.status}, Location: {self.location}, Battery: {self.battery}%"

# Define agents lazily inside a function
def get_agents():
    llm = GroqLLM()
    return {
        "controller": DisasterResponseAgent("Controller", "central coordinator", ["task allocation", "communication"], llm),
        "rescue": DisasterResponseAgent("Rescue-1", "on-site rescue", ["victim extraction", "first aid"], llm),
        "drone": DisasterResponseAgent("Drone-1", "aerial drone", ["surveillance", "victim detection"], llm, 
                                       backups=[DisasterResponseAgent("Drone-2", "aerial drone", ["surveillance", "victim detection"], llm)]),
        "medical": DisasterResponseAgent("Medical-1", "medical support", ["treatment", "transport"], llm),
        "assess": DisasterResponseAgent("Assess-1", "damage assessor", ["structural analysis", "hazard detection"], llm),
        "supplies": DisasterResponseAgent("Supplies-1", "supply delivery", ["food", "water", "medical supplies"], llm, 
                                          backups=[DisasterResponseAgent("Supplies-2", "supply delivery", ["food", "water", "medical supplies"], llm)]),
        "routes": DisasterResponseAgent("Routes-1", "road coordinator", ["route planning", "barricades"], llm)
    }