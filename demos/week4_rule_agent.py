import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rule_based_agent import RuleBasedAgent
import json

def run_demo():
    print("=== Phase 2: Heuristic Rule-Based Agent ===")
    # Simulate a loop-heavy program
    features = {
        "loop_density": 0.8,
        "arithmetic_ratio": 0.2,
        "mem_ops_ratio": 0.6
    }
    
    agent = RuleBasedAgent()
    agent.observation = features # Set observation instead of passing to act
    action = agent.act()
    
    print(f"\n[Environment] Detected High Loop Density (0.8)")
    print(f"[Agent Decision] Suggested Pass: {action}")
    print("\nReasoning: Standard heuristics favor loop unrolling for high-density loops.")

if __name__ == "__main__":
    run_demo()
