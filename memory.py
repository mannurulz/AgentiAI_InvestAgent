# memory.py
import json

class AgentMemory:
    def __init__(self, filename="agent_memory.json"):
        self.filename = filename
        self.data = self._load_memory()

    def _load_memory(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {self.filename}. Starting with empty memory.")
            return {}

    def _save_memory(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._save_memory()

    def update_company_data(self, symbol: str, data: dict):
        if "companies" not in self.data:
            self.data["companies"] = {}
        self.data["companies"][symbol] = data
        self._save_memory()

    def get_company_data(self, symbol: str):
        return self.data.get("companies", {}).get(symbol)