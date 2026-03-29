import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_agent import DQNAgent
import numpy as np

def run_demo():
    print("=== Phase 3: Reinforcement Learning (DQN) Inference ===")
    action_space = ["loop_unroll", "inline", "vectorize", "dce"]
    agent = DQNAgent(action_space=action_space, state_dim=10)
    
    # Mock some basic features
    features = {
        "arithmetic_ratio": 0.7,
        "mem_ops_ratio": 0.1,
        "loop_density": 0.4,
        "bb_count": 50
    }
    
    print(f"[System] State features: {features}")
    action = agent.choose_action(features)
    print(f"\n[DQN Agent] Predicted optimal pass: {action}")
    print("\nMotivation: Moving beyond fixed rules to data-driven 'Phase Ordering' using Bellman Optimality.")

if __name__ == "__main__":
    run_demo()
