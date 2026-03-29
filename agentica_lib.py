import json
import inspect

class Environment:
    """
    Mock Environment that represents the compiler workspace.
    """
    def __init__(self, program_path):
        self.program_path = program_path
        self.features = {}

    def get_features(self):
        """
        Returns the current observation of the environment.
        In a real scenario, this would run the feature extractor.
        """
        return self.features
    
    def set_features(self, features):
        self.features = features

class Agent:
    """
    Mock Agent that observes the environment and selects an action.
    """
    def __init__(self, name="Agent"):
        self.name = name
        self.env = None
        self.tools = {}

    def connect(self, env):
        self.env = env
        print(f"[{self.name}] Connected to environment: {env.program_path}")

    def register_tool(self, name, func):
        self.tools[name] = func

    def observe(self, features):
        self.observation = features
        print(f"[{self.name}] Observed features: {json.dumps(features)}")

    def act(self):
        """
        Simple logic to select a pass based on features.
        This simulates the 'AI' decision making.
        """
        
        suggested_pass = None
        
        loops = self.observation.get("loops", 0)
        
        if loops > 0:
            suggested_pass = "loop_unroll"
        elif self.observation.get("functions", 0) > 5:
            suggested_pass = "inline_functions"
        else:
            suggested_pass = "vectorize"

        print(f"[{self.name}] Selected pass: {suggested_pass}")
        
        return suggested_pass
