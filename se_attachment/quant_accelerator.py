import sys
import os

# Link to core AegisOpt modules for compilation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mape_loop import MAPEManager
from telemetry_db import TelemetryDBMS

def run_quant_accelerator(silent=False):
    if not silent:
        print("\n=======================================================")
        print(" AegisOpt Quant Accelerator - Micro-Latency HFT Module")
        print(" SE Constraint: Financial Domain | DBMS Telemetry Active")
        print("=======================================================\n")

    target_kernel = os.path.join(os.path.dirname(__file__), "fintech_kernels", "black_scholes.cpp")
    
    if not os.path.exists(target_kernel):
        if not silent: print(f"[Error] Fintech kernel {target_kernel} missing.")
        return

    # Unify on root directory db
    db = TelemetryDBMS(db_path="hft_telemetry.db")
    
    if not silent: print(f"[Cloud Coordinator] Initializing HFT Pipeline for {os.path.basename(target_kernel)}...")
    
    # Temporarily redirect stdout if silent
    if silent:
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
    try:
        manager = MAPEManager(program_path=target_kernel, security_mode=True)
        baseline_latency = manager.run_baseline()
        manager.run_sequential_cycle(agent_type="RL", steps=3)
        
        history = manager.history.history
        if not history: return
            
        final_latency = history[-1]["latency"]
        pass_sequence = ", ".join([h["action"] for h in history[1:]])
        improvement = ((baseline_latency - final_latency) / baseline_latency) * 100

        db.log_optimization("black_scholes_options_pricing", "RL_Agent_Quant", pass_sequence, baseline_latency, final_latency, True)
    finally:
        if silent:
            sys.stdout.close()
            sys.stdout = old_stdout

    db.close()

if __name__ == "__main__":
    run_quant_accelerator()

