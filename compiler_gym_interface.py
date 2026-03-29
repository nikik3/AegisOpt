import os
import subprocess
import numpy as np
from feature_extractor import extract_features
from oracle import PerformanceOracle

class CompilerEnv:
    """
    Research-Grade: CompilerGym-Compatible Environment Wrapper.
    Follows the OpenAI Gym API for seamless integration with RL frameworks.
    """
    def __init__(self, program_path, actions):
        self.program_path = program_path
        self.actions = actions # List of pass names
        self.oracle = PerformanceOracle(binary_path="./program_opt")
        self.active_ll = self.program_path.replace(".cpp", "_active.ll")
        self.baseline_latency = None
        self.current_latency = None
        self.steps_taken = 0

    def reset(self):
        """Resets the environment to the baseline (-O3) state."""
        self.steps_taken = 0
        if os.path.exists(self.active_ll):
            os.remove(self.active_ll)
        
        # Compile baseline
        subprocess.run(f"g++ -O3 {self.program_path} -o program_opt", shell=True, check=True)
        self.baseline_latency = self.oracle.measure()
        self.current_latency = self.baseline_latency
        
        return self._get_observation()

    def _get_observation(self):
        """Returns the 'Autophase' style feature vector."""
        features = extract_features(self.program_path)
        # Normalized vector (Matching DQNAgent requirements)
        v = [
            features.get("arithmetic_ratio", 0.5),
            features.get("mem_ops_ratio", 0.5),
            features.get("branch_ratio", 0.1),
            features.get("bb_count", 0) / 100.0,
            float(features.get("is_llvm", False)),
            features.get("loop_density", 0) * 10.0,
            # Hardware features (placeholder for architectural context)
            0.0, 0.0, 0.0, 0.25 
        ]
        return np.array(v)

    def step(self, action_idx):
        """Applies an optimization pass and returns (obs, reward, done, info)."""
        action_name = self.actions[action_idx]
        self.steps_taken += 1
        
        # Execute the optimization (simulated via existing tools)
        from optimizer_setup import loop_unroll, vectorize, inline_functions, dce, licm, strip
        tool_map = {
            "loop_unroll": loop_unroll,
            "vectorize": vectorize,
            "inline_functions": inline_functions,
            "dce": dce,
            "licm": licm,
            "strip": strip
        }
        
        class MockEnv:
            def __init__(self, path): self.program_path = path

        if action_name in tool_map:
            tool_map[action_name](MockEnv(self.program_path))
        
        # Measure
        new_latency = self.oracle.measure()
        reward = (self.current_latency - new_latency) / self.baseline_latency
        self.current_latency = new_latency
        
        obs = self._get_observation()
        done = self.steps_taken >= 5 # Episode limit
        
        info = {
            "action": action_name,
            "latency": new_latency,
            "improvement": (self.baseline_latency - new_latency) / self.baseline_latency
        }
        
        return obs, reward, done, info

if __name__ == "__main__":
    # Test Interface
    actions = ["loop_unroll", "vectorize", "inline_functions", "dce", "licm", "strip"]
    env = CompilerEnv("program.cpp", actions)
    obs = env.reset()
    print(f"Initial Observation: {obs}")
    new_obs, reward, done, info = env.step(1) # Apply vectorize
    print(f"Reward: {reward}, Done: {done}, Info: {info}")
