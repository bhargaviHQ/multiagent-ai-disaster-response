import random
from datetime import datetime

class DisasterEnvironment:
    def __init__(self):
        self.time = datetime.now()
        self.disaster_type = random.choice(["earthquake", "flood", "wildfire"])
        self.affected_areas = []
        self.blocked_routes = []
        self.victim_locations = []
        self.supply_needs = []
        self.completed_tasks = {"rescued": [], "supplied": []}
        self.initialize_environment()

    def initialize_environment(self):
        for _ in range(random.randint(5, 10)):
            x, y = random.randint(0, 100), random.randint(0, 100)
            self.affected_areas.append((x, y))
            if random.random() > 0.6: self.blocked_routes.append((x, y))
            if random.random() > 0.5: self.victim_locations.append((x, y))
            if random.random() > 0.4: self.supply_needs.append((x, y, random.choice(["medical", "food", "water"])))

    def update_environment(self):
        if self.disaster_type == "wildfire":
            new_areas = []
            for x, y in self.affected_areas:
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    new_x, new_y = x+dx, y+dy
                    if 0 <= new_x <= 100 and 0 <= new_y <= 100 and random.random() > 0.8:
                        new_areas.append((new_x, new_y))
            self.affected_areas.extend(new_areas)
            if random.random() > 0.7:
                self.victim_locations.append(random.choice(self.affected_areas))
        elif self.disaster_type == "flood":
            self.blocked_routes = [(x, y-1) for x, y in self.blocked_routes if 0 <= y-1 <= 100]
            if random.random() > 0.6:
                self.supply_needs.append((random.randint(0, 100), random.randint(0, 100), "water"))
        elif self.disaster_type == "earthquake":
            if random.random() > 0.5:
                new_block = random.choice(self.affected_areas)
                self.blocked_routes.append(new_block)
                self.victim_locations.append(new_block)
        self.time = datetime.now()

    def get_report(self):
        return {
            "disaster_type": self.disaster_type,
            "affected_areas": self.affected_areas,
            "blocked_routes": self.blocked_routes,
            "victim_locations": [loc for loc in self.victim_locations if loc not in self.completed_tasks["rescued"]],
            "supply_needs": [need for need in self.supply_needs if need not in self.completed_tasks["supplied"]]
        }