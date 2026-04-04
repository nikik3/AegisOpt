import os
import sys
# Add parent directory to path to allow importing core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mape_loop import MAPEManager
from hardware_profiler import HardwareProfiler
import json

def run_demo(target_file="program.cpp"):
    print("=== Phase 5: Hardware-Aware RL Generalization ===")
    
    if not os.path.exists(target_file):
        print(f"[Error] Target file {target_file} not found.")
        return

    # 1. Hardware Detection
    hp = HardwareProfiler()
    hw_vector = hp.get_feature_vector()
    print(f"[Hardware] Detected Capabilities: {hp.features}")
    print(f"[Hardware] Feature Vector: {hw_vector}")

    # 2. Setup the Orchestrator with the target file
    print(f"\n[MAPE] Loading AegisOpt Control Plane for '{target_file}'...")
    manager = MAPEManager(program_path=target_file, security_mode=True)
    
    # 3. Establish Baseline
    baseline = manager.run_baseline()
    
    # 4. Run Sequential Optimization (Generalization)
    # The RL agent will use its pre-trained brain (dqn_policy.npz)
    print("\n[AI Agent] Applying Global RL Policy to the current environment...")
    manager.run_sequential_cycle(agent_type="RL", steps=3)
    
    # 5. Result Verification
    history = manager.history.history
    final_lat = history[-1]["latency"]
    improvement = ((baseline - final_lat) / baseline) * 100
    
    print(f"\n--- WEEK 11 FINAL REPORT ---")
    print(f"Target Program:    {target_file}")
    print(f"Hardware Context:  {hp.features}")
    print(f"Baseline -O3:     {baseline:.4f}s")
    print(f"AegisOpt Optimized: {final_lat:.4f}s")
    print(f"Efficiency Gain:   +{improvement:.2f}%")
    print(f"============================")

if __name__ == "__main__":
    target = "program.cpp"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    run_demo(target)
