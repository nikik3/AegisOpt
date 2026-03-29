from rl_agent import DQNAgent
from feature_extractor import extract_features
import random
import os
import time

def train():
    print("--- AegisOpt Professional Training: DQNAgent Multi-Benchmark Regime ---")
    
    actions = ["loop_unroll", "vectorize", "inline_functions", "licm", "dce", "strip"]
    agent = DQNAgent(actions)
    
    benchmarks = ["program.cpp", "matrix_mul.cpp", "sorting.cpp", "vulnerable_code.cpp"]
    
    # 1. Ensure all benchmarks are compiled baseline
    from mape_loop import MAPEManager
    managers = {prog: MAPEManager(program_path=prog) for prog in benchmarks}
    baselines = {}
    for prog, manager in managers.items():
        baselines[prog] = {
            "latency": manager.run_baseline(),
            "size": manager.oracle.get_binary_size()
        }

    print("\nStarting Deep Reinforcement Learning (500 episodes)...")
    
    for episode in range(1, 501):
        target_prog = random.choice(benchmarks)
        manager = managers[target_prog]
        
        # 1. Observe State
        features = extract_features(target_prog)
        
        # 2. Choose Action
        action = agent.choose_action(features)
        
        # 3. Apply Action (Execute)
        if action in manager.tools:
            manager.tools[action](manager.oracle) # Use a mock env-like object

        # 4. Measure Reward
        # Reward = % Latency Improvement - % Size Increase
        new_latency = manager.oracle.measure(iterations=2)
        new_size = manager.oracle.get_binary_size()
        
        b = baselines[target_prog]
        latency_diff = (b["latency"] - new_latency) / b["latency"]
        size_diff = (new_size - b["size"]) / b["size"]
        
        reward_metrics = {"latency_diff": latency_diff, "size_diff": size_diff}
        
        # 5. Learn (DQN Step)
        next_features = extract_features(target_prog)
        agent.learn(features, action, reward_metrics, next_features)
        
        if episode % 50 == 0:
            agent.update_target_network()
            print(f"[Episode {episode}] Epsilon: {agent.epsilon:.4f} | Target: {target_prog} | Latency Imp: {latency_diff*100:.2f}%")
            
    print("\nTraining Complete. DQNAgent converged.")
    agent.save_policy("dqn_weights.npz")

if __name__ == "__main__":
    train()
