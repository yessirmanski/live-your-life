import tkinter as tk
from tkinter import ttk, messagebox
import random

# Constants
CELL_SIZE = 15
MIN_GRID = 10
MAX_GRID = 100
GRID_STEP = 10
INITIAL_GRID_SIZE = 50

RESOURCE_TYPES = ['food', 'wood', 'stone', 'gold', 'forbidden_fruit']
LIVESTOCK_TYPES = ['cow', 'pig', 'chicken']
BIOMES = ['forest', 'plains', 'mountains', 'river']

class Tile:
    """Represents a single tile in the world."""
    def __init__(self, biome):
        self.biome = biome
        self.resource = None
        self.livestock = None
        self.building = None
        self.territory = None  # Belonging to a faction
        self.regrow_counter = 0

    def random_init(self):
        biome_weights = {'forest': [80, 10, 5, 5], 'plains': [40, 30, 10, 20], 'mountains': [5, 10, 50, 35]}
        weights = biome_weights.get(self.biome, [25, 25, 25, 25])
        self.resource = random.choices(
            [None, 'food', 'wood', 'stone', 'gold'],
            weights=weights + [5])[0]
        self.livestock = random.choice(LIVESTOCK_TYPES + [None] * 10)

    def regrow(self):
        if self.resource is None:
            self.regrow_counter += 1
            if self.regrow_counter > 15:
                biome_weights = {'forest': [70, 20, 5, 5], 'plains': [50, 30, 10, 10], 'mountains': [5, 5, 60, 30]}
                weights = biome_weights.get(self.biome, [25, 25, 25, 25])
                self.resource = random.choices(['food', 'wood', 'stone', 'gold'], weights=weights)[0]
                self.regrow_counter = 0

class Agent:
    """Represents an agent in the simulation."""
    def __init__(self, name, x, y, gender, faction=None):
        self.name = name
        self.x = x
        self.y = y
        self.gender = gender
        self.faction = faction
        self.color = 'blue' if gender == 'male' else 'pink'
        self.inventory = {'food': 1, 'wood': 0, 'stone': 0, 'gold': 0, 'weapons': 0}
        self.energy = 10
        self.mood = "neutral"

    def move(self, width, height):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
        self.x = max(0, min(width - 1, self.x + dx))
        self.y = max(0, min(height - 1, self.y + dy))

class Faction:
    """Represents a faction in the world."""
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.leader = None
        self.members = []
        self.territories = []
        self.resources = {'food': 0, 'wood': 0, 'stone': 0, 'gold': 0}
        self.reputation = 0

    def collect_taxes(self):
        total_tax = sum(len(agent.inventory) for agent in self.members)
        self.resources['gold'] += total_tax

class CivilizationSimApp:
    """Main simulation application."""
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Civilization Simulator")
        self.grid_size = INITIAL_GRID_SIZE
        self.world = []
        self.agents = []
        self.factions = []
        self.setup_ui()
        self.create_world()
        self.update_loop()

    def setup_ui(self):
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(self.mainframe, width=self.grid_size * CELL_SIZE, height=self.grid_size * CELL_SIZE, bg='white')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.control_panel = ttk.Frame(self.mainframe, width=200)
        self.control_panel.grid(row=0, column=1, sticky='ns')

        self.log_label = ttk.Label(self.control_panel, text="Action Log:")
        self.log_label.pack()

        self.log_text = tk.Text(self.control_panel, height=15, width=30, state='disabled')
        self.log_text.pack()

        self.faction_panel = ttk.Frame(self.control_panel)
        self.faction_panel.pack(fill='x', pady=10)

    def log(self, message):
        self.log_text['state'] = 'normal'
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text['state'] = 'disabled'

    def create_world(self):
        biomes = random.choices(BIOMES, k=self.grid_size)
        self.world = [[Tile(random.choice(biomes)) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for row in self.world:
            for tile in row:
                tile.random_init()
        self.create_agents()
        self.create_factions()

    def create_agents(self):
        for i in range(5):  # Small number for demo
            self.agents.append(Agent(f"Agent{i}", random.randint(0, self.grid_size - 1),
                                     random.randint(0, self.grid_size - 1),
                                     random.choice(['male', 'female'])))

    def create_factions(self):
        faction_colors = ['red', 'green', 'blue', 'yellow']
        for i, color in enumerate(faction_colors):
            faction = Faction(f"Faction{i}", color)
            self.factions.append(faction)
            self.log(f"Faction created: {faction.name}")

    def update_loop(self):
        self.run_turn()
        self.root.after(1000, self.update_loop)

    def run_turn(self):
        for agent in self.agents:
            agent.move(self.grid_size, self.grid_size)
        self.log("Agents moved.")
        self.update_ui()

    def update_ui(self):
        self.canvas.delete("all")
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                tile = self.world[y][x]
                color = 'white'
                if tile.resource == 'food':
                    color = 'lightgreen'
                elif tile.resource == 'wood':
                    color = 'brown'
                elif tile.resource == 'stone':
                    color = 'gray'
                elif tile.resource == 'gold':
                    color = 'yellow'
                self.canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, 
                                             x * CELL_SIZE + CELL_SIZE, y * CELL_SIZE + CELL_SIZE,
                                             fill=color, outline='black')

        for agent in self.agents:
            ax, ay = agent.x * CELL_SIZE + 2, agent.y * CELL_SIZE + 2
            self.canvas.create_oval(ax, ay, ax + CELL_SIZE - 4, ay + CELL_SIZE - 4, fill=agent.color)

if __name__ == "__main__":
    root = tk.Tk()
    app = CivilizationSimApp(root)
    root.mainloop()
