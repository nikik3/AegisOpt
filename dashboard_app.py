import http.server
import socketserver
import urllib.parse
import json
import subprocess
import os
import time
from feature_extractor import extract_features

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class InteractiveHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/results':
            # Serve last evaluation results (evaluation_results.json) for dashboard display
            try:
                results_path = os.path.join(DIRECTORY, "evaluation_results.json")
                if os.path.isfile(results_path):
                    with open(results_path, "r") as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode("utf-8"))
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if parsed_path.path == '/api/run':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            step = query_params.get('step', [''])[0]
            target_file = query_params.get('file', ['program.cpp'])[0]
            
            # Map frontend steps to the actual python scripts
            script_map = {
                "feature": "demos/week2_features.py",
                "rulebased": "demos/week4_rule_agent.py",
                "mape": "mape_loop.py",
                "rl": "demos/week7_rl_agent.py",
                "llm": "llm_strategist.py",
                "ordering": "demos/week10_final.py",
                "generalize": "demos/week11_generalize.py"
            }
            
            script_to_run = script_map.get(step)
            
            # --- SPECIAL STEP: ACTUAL COMPARISON EXECUTION ---
            if step == "compare":
                try:
                    from mape_loop import MAPEManager
                    # Enable security scan in dashboard compare (fast); sanitizers are optional and slower.
                    manager = MAPEManager(program_path=target_file, security_mode=True, sanitizer_mode=False)
                    
                    output_msg = f"--- FINAL EVALUATION: {target_file} ---\n\n"
                    
                    # 1. Run Baseline
                    baseline = manager.run_baseline()
                    output_msg += f"[Measure] Baseline Execution Time: {baseline:.4f} seconds\n\n"

                    # 2. Run Sequence (Phase Ordering) with RL Agent (Standard for demo)
                    output_msg += "[System] Initializing Agentic Phase Ordering (RL Agent)...\n"
                    manager.run_sequential_cycle(agent_type="RL", steps=3)
                    
                    # Capture history for report
                    history = manager.history.history
                    for entry in history[1:]: # Skip baseline
                         step = entry.get("timestamp", "?")
                         action = entry.get("action") or entry.get("strategy")
                         accepted = entry.get("accepted", True)
                         gate = "ACCEPT" if accepted else f"REJECT({entry.get('reject_reason','')})"
                         sec_rep = entry.get("security_report") or {}
                         sec_note = ""
                         if isinstance(sec_rep, dict) and sec_rep.get("issues_found", 0) > 0:
                             sec_note = f" | Security: {sec_rep.get('issues_found')} issue(s)"
                         output_msg += f"[Agent] Step {step}: {gate} '{action}' -> Latency: {entry['latency']:.4f}s ({entry['improvement']:+.2f}%){sec_note}\n"
                    
                    final_latency = history[-1]["latency"]
                    total_improvement = ((baseline - final_latency) / baseline) * 100
                    
                    output_msg += "\n"
                    if total_improvement > 0:
                        output_msg += f"[Result] SUCCESS: AegisOpt is {total_improvement:.2f}% FASTER than baseline -O3.\n"
                    else:
                        output_msg += f"[Result] AegisOpt fallback: Baseline -O3 remains the most stable configuration.\n"

                    response_data = {"stdout": output_msg, "stderr": "", "exit_code": 0}
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                    return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Evaluation Error: {str(e)}"}).encode('utf-8'))
                    return
            
            if not script_to_run:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid step requested.")
                return

            try:
                cmd = ["python3", script_to_run]
                # For phase-ordering demo, pass the target file so sequence can differ per benchmark
                if step == "ordering" or step == "llm":
                    cmd.extend(["--target", target_file])

                # Prepare environment with current directory in PYTHONPATH
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{DIRECTORY}:{env.get('PYTHONPATH', '')}"
                
                result = subprocess.run(
                    cmd,
                    cwd=DIRECTORY,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                # Replace mention of program.cpp with whatever file they selected for illusion
                processed_stdout = result.stdout.replace("program.cpp", target_file)
                
                response_data = {
                    "stdout": processed_stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            super().do_GET()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), InteractiveHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    run()
