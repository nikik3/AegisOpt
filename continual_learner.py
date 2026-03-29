import json
import os
import time

class ContinualLearner:
    """
    Week 13: Continual Learning Pipeline.
    Enables agents to learn from historical executions via an experience replay database.
    """
    def __init__(self, db_path="knowledge_base.json"):
        self.db_path = db_path
        self.memory = self._load()
        
    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return []

    def ingest_telemetry(self, state, action, reward):
        print(f"[ContinualLearner] Archiving execution: {action} -> {reward:+.2f}")
        entry = {
            "timestamp": time.time(),
            "state": state,
            "action": action,
            "reward": reward
        }
        self.memory.append(entry)
        with open(self.db_path, 'w') as f:
            json.dump(self.memory, f, indent=4)
        print(f"[System] Shared Knowledge Base updated ({len(self.memory)} records).")
