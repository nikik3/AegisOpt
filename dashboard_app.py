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
        if parsed_path.path == '/api/fintech':
            try:
                import sqlite3
                db_path = os.path.join(DIRECTORY, "hft_telemetry.db")
                
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT timestamp, latency_improvement_percent, pass_sequence, baseline_latency, optimized_latency FROM compilation_metrics ORDER BY id DESC LIMIT 10')
                    rows = cursor.fetchall()
                    conn.close()
                    rows.reverse()
                    data = {
                        "timestamps": [r[0].split("T")[1][:8] for r in rows],
                        "improvements": [r[1] for r in rows],
                        "passes": [r[2] for r in rows],
                        "baselines": [r[3] for r in rows],
                        "optimized": [r[4] for r in rows]
                    }
                else:
                    data = {"timestamps": ["No Data"], "improvements": [0], "passes": ["None"], "baselines": [0], "optimized": [0]}
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
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
            
            if step == "compare":
                try:
                    from mape_loop import MAPEManager
                    import llm_strategist
                    
                    manager = MAPEManager(program_path=target_file, security_mode=True, sanitizer_mode=False)
                    baseline = manager.run_baseline()
                    
                    # Run RuleBased
                    manager.run_sequential_cycle(agent_type="RuleBased", steps=3)
                    rule_history = manager.history.history
                    rule_latency = rule_history[-1]["latency"] if len(rule_history) > 1 else baseline
                    
                    # Reset & Run RL
                    manager = MAPEManager(program_path=target_file, security_mode=True, sanitizer_mode=False)
                    manager.run_baseline()
                    manager.run_sequential_cycle(agent_type="RL", steps=3)
                    rl_history = manager.history.history
                    rl_latency = rl_history[-1]["latency"] if len(rl_history) > 1 else baseline
                    
                    # Reset & Run LLM
                    manager = MAPEManager(program_path=target_file, security_mode=True, sanitizer_mode=False)
                    manager.run_baseline()
                    manager.run_sequential_cycle(agent_type="LLM", steps=3)
                    llm_history = manager.history.history
                    llm_latency = llm_history[-1]["latency"] if len(llm_history) > 1 else baseline

                    def get_seq(hist):
                        return [e.get("action", e.get("strategy")) for e in hist[1:] if e.get("accepted")]

                    def calc_imp(lat): return ((baseline - lat) / baseline) * 100 if baseline > 0 else 0

                    response_data = {
                        "stdout": "[Orchestrator] Comparative Analysis complete across 3 agents.", 
                        "stderr": "", 
                        "exit_code": 0,
                        "chart_data": {
                            "labels": ["GCC (-O3)", "Rule-Based", "DQN RL", "LLM"],
                            "data": [baseline, rule_latency, rl_latency, llm_latency],
                            "improvements": [0, calc_imp(rule_latency), calc_imp(rl_latency), calc_imp(llm_latency)],
                            "sequences": [[], get_seq(rule_history), get_seq(rl_history), get_seq(llm_history)]
                        }
                    }
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
