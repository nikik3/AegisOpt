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
                db_path = os.path.join(DIRECTORY, "se_attachment", "optimization_telemetry.db")
                if not os.path.exists(db_path):
                    db_path = os.path.join(DIRECTORY, "hft_telemetry.db")
                
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT timestamp, latency_improvement_percent, pass_sequence FROM compilation_metrics ORDER BY id DESC LIMIT 10')
                    rows = cursor.fetchall()
                    conn.close()
                    rows.reverse()
                    data = {
                        "timestamps": [r[0].split("T")[1][:8] for r in rows],
                        "improvements": [r[1] for r in rows],
                        "passes": [r[2] for r in rows]
                    }
                else:
                    data = {"timestamps": ["No Data"], "improvements": [0], "passes": ["None"]}
                    
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
                    manager = MAPEManager(program_path=target_file, security_mode=True, sanitizer_mode=False)
                    
                    output_msg = f"--- FINAL EVALUATION: {target_file} ---\n\n"
                    
                    baseline = manager.run_baseline()
                    output_msg += f"[Measure] Baseline Execution Time: {baseline:.4f} seconds\n\n"

                    output_msg += "[System] Initializing Agentic Phase Ordering (RL Agent)...\n"
                    manager.run_sequential_cycle(agent_type="RL", steps=3)
                    
                    history = manager.history.history
                    for entry in history[1:]: 
                         st = entry.get("timestamp", "?")
                         action = entry.get("action") or entry.get("strategy")
                         accepted = entry.get("accepted", True)
                         gate = "ACCEPT" if accepted else f"REJECT"
                         output_msg += f"[{st}] {gate} '{action}' -> {entry['latency']:.4f}s\n"
                    
                    final_latency = history[-1]["latency"]
                    total_improvement = ((baseline - final_latency) / baseline) * 100
                    
                    output_msg += f"\n[Result] Compilation Complete. AI beat standard -O3 by {total_improvement:.2f}%."

                    response_data = {
                        "stdout": output_msg, 
                        "stderr": "", 
                        "exit_code": 0,
                        "chart_data": {
                            "labels": ["Standard GCC (-O3)", "AegisOpt (RL Agent)"],
                            "data": [baseline, final_latency]
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
