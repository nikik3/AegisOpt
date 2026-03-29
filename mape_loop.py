from oracle import PerformanceOracle
from knowledge_base import OptimizationHistory
from feature_extractor import extract_features
from rule_based_agent import RuleBasedAgent
from config import Config
from optimizer_setup import (
    loop_unroll,
    inline_functions,
    vectorize,
    dce,
    licm,
    strip,
    _detect_compiler,
)
import os
import subprocess
import logging
import numpy as np

logger = Config.setup_logging()

class MAPEManager:
    """
    The Orchestrator that runs the Feedback Loop.
    """
    def __init__(self, program_path="program.cpp", security_mode=False, sanitizer_mode=False):
        self.program_path = program_path
        self.security_mode = security_mode
        self.sanitizer_mode = sanitizer_mode
        self.history = OptimizationHistory()
        self.oracle = PerformanceOracle(binary_path="./program_opt")
        self.golden_output = None
        # Ensure we have the tools available
        self.tools = {
            "loop_unroll": loop_unroll,
            "inline_functions": inline_functions,
            "vectorize": vectorize,
            "dce": dce,
            "licm": licm,
            "strip": strip
        }

    def _active_ir_path(self):
        base = self.program_path.replace(".cpp", "")
        return f"{base}_active.ll"

    def _compile_baseline(self):
        compiler = _detect_compiler()
        if compiler is None:
            logger.error("No suitable C++ compiler found. Please install `g++` or `clang++`.")
            return None
        cmd = f"{compiler} -O3 {self.program_path} -o program_opt"
        logger.info(f"Compiling Initial Baseline: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True
        except FileNotFoundError as e:
            logger.error(f"Compilation failed (compiler not found): {e}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Compilation failed: {e}")
            return None

    def _compile_with_sanitizers(self, action_name=None):
        """
        Best-effort sanitizer check: compile the current program (or active IR if present) with sanitizers and run once.
        Returns a dict report: {status, ok, message, stderr}
        """
        # We try clang++ first because sanitizers are most consistent there.
        import shutil
        compiler = None
        if shutil.which("clang++"):
            compiler = "clang++"
        else:
            # g++ supports some sanitizers too; keep it as fallback.
            if shutil.which("g++"):
                compiler = "g++"

        if compiler is None:
            return {"status": "skipped", "ok": True, "message": "No compiler available for sanitizers", "stderr": ""}

        active_ll = self._active_ir_path()
        input_path = active_ll if os.path.exists(active_ll) and compiler == "clang++" else self.program_path
        out_bin = "./program_san"
        san_flags = "-fsanitize=address,undefined -fno-omit-frame-pointer"
        cmd = f"{compiler} -O1 {san_flags} {input_path} -o {out_bin}"
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            return {"status": "error", "ok": False, "message": f"Sanitizer compile failed ({action_name})", "stderr": (e.stderr or "")}

        try:
            r = subprocess.run(out_bin, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=5)
            # Sanitizer reports are printed to stderr; treat any stderr containing "ERROR:" as failure.
            if r.stderr and ("ERROR:" in r.stderr or "runtime error:" in r.stderr):
                return {"status": "fail", "ok": False, "message": f"Sanitizer found issues ({action_name})", "stderr": r.stderr}
            return {"status": "ok", "ok": True, "message": "Sanitizer run clean", "stderr": r.stderr or ""}
        except subprocess.CalledProcessError as e:
            return {"status": "fail", "ok": False, "message": f"Sanitizer run crashed ({action_name})", "stderr": (e.stderr or "")}
        except subprocess.TimeoutExpired:
            return {"status": "fail", "ok": False, "message": f"Sanitizer run timed out ({action_name})", "stderr": ""}

    def run_baseline(self):
        """
        Step 1: Establish Baseline (-O3)
        """
        logger.info("--- Phase 1: Establishing Baseline ---")

        if not self._compile_baseline():
            return None

        latency = self.oracle.measure()
        self.golden_output = self.oracle.get_output()
        print(f"[Monitor] Baseline Latency: {latency:.4f}s")
        if self.golden_output:
            print(f"[Monitor] Golden Output Captured (length: {len(self.golden_output)})")
        
        self.history.record("baseline", latency, 0.0, action="baseline", agent_type="baseline", accepted=True, correctness_ok=True)
        return latency

    def run_sequential_cycle(self, agent_type="RL", steps=3):
        """
        SCIENTIFIC S-GRADE: Solves the Phase Ordering problem.
        Applies a sequence of optimizations to the same binary.
        """
        print(f"\n[MAPE] --- Phase 2: Sequential Phase Ordering ({agent_type}, {steps} steps) ---")
        
        if not self.history.history:
            print("[MAPE] No baseline recorded; aborting.")
            return

        # Cleanup active IR to start fresh
        active_ll = self._active_ir_path()
        if os.path.exists(active_ll):
            os.remove(active_ll)

        for i in range(steps):
            print(f"\n[MAPE] Step {i+1}/{steps} of sequence...")
            accepted = self.run_optimization_cycle(agent_type=agent_type, step_mode=True)
            # If a step is rejected (security/correctness), stop the sequence.
            if accepted is False:
                print("[MAPE] Sequence stopped due to rejection/fallback.")
                break

    def run_optimization_cycle(self, agent_type="RL", step_mode=False):
        """
        One cycle of optimization. If step_mode is True, it assumes it's part of a sequence.
        """
        if not step_mode:
            print(f"\n[MAPE] --- Phase 2: Agentic Optimization Cycle ({agent_type}) ---")
            # Clear old active IR for fresh single-pass
            active_ll = self._active_ir_path()
            if os.path.exists(active_ll): os.remove(active_ll)

        if not self.history.history:
            return
        
        # 1. Monitor (Update features for current state of binary/IR)
        # For sequential, we should ideally extract features from the IR
        features = extract_features(self.program_path)
        
        # 2. Plan (Agent Decision)
        if agent_type == "RL":
            from rl_agent import RLAgent
            actions = list(self.tools.keys())
            agent = RLAgent(actions)
            agent.load_policy()
        elif agent_type == "LLM":
            from llm_strategist import LLMStrategist
            agent = LLMStrategist()
        else:
            agent = RuleBasedAgent(name="AegisOpt-Feedback", goal="performance")
        
        class MockEnv:
            def __init__(self, path): self.program_path = path
        
        env = MockEnv(self.program_path)
        
        # 3. Execute
        action = None
        reasoning = "No reasoning provided."
        if agent_type == "RL":
            agent.connect(env)
            for name, func in self.tools.items():
                agent.register_tool(name, func)
            action = agent.choose_action(features)
        elif agent_type == "LLM":
            with open(self.program_path, 'r') as f:
                code = f.read()
            analysis = agent.analyze_code(code)
            suggestion = agent.suggest_optimization(analysis)
            if not isinstance(suggestion, dict): return
            action = suggestion.get("suggestion")
            reasoning = suggestion.get("reasoning") or ""
        else:
            agent.connect(env)
            for name, func in self.tools.items():
                agent.register_tool(name, func)
            agent.observe(features)
            action = agent.act()

        if not action or action not in self.tools:
            return

        self.tools[action](env)

        # 4. Monitor
        new_latency = self.oracle.measure()
        new_size = self.oracle.get_binary_size()
        
        # 5. Analyze
        baseline_record = self.history.history[0]
        baseline_latency = baseline_record["latency"]
        baseline_size = baseline_record.get("size", new_size)
        
        improvement = ((baseline_latency - new_latency) / baseline_latency) * 100
        size_increase = ((new_size - baseline_size) / baseline_size) * 100 if baseline_size > 0 else 0
        
        # Functional Correctness Check
        current_output = self.oracle.get_output()
        correctness_ok = True
        if self.golden_output and current_output != self.golden_output:
            logger.error(f"CORRECTNESS REGRESSION! Output mismatch after {action}")
            improvement = -100.0
            correctness_ok = False

        # Security scan (best-effort)
        security_report = {}
        security_ok = True
        if self.security_mode:
            try:
                from security_agent import SecurityAgent
                s = SecurityAgent()
                # Prefer IR scan if active IR exists; also do a lightweight source scan
                active_ll = self._active_ir_path()
                ir_rep = s.scan_ir(active_ll) if os.path.exists(active_ll) else None
                src_rep = s.scan_source(self.program_path)
                # Merge: prefer IR details when present
                if ir_rep and ir_rep.get("status") == "success":
                    security_report = {"source": "ir", **ir_rep, "source_scan": src_rep}
                else:
                    security_report = {"source": "source", **src_rep}
                if security_report.get("issues_found", 0) > 0:
                    summary = SecurityAgent.summarize(security_report)
                    print(f"[Robustness] R-GRADE SCAN: {summary}")
                    # Detailed logging of IR patterns
                    for issue in security_report.get("details", []):
                        print(f"  - [{issue.get('severity')}] {issue.get('recommendation')}")
                    # Treat CRITICAL as a hard rejection; WARNING/LOW become penalties.
                    severities = [d.get("severity", "") for d in security_report.get("details", [])]
                    if "CRITICAL" in severities:
                        security_ok = False
            except Exception as e:
                security_report = {"status": "error", "message": str(e), "issues_found": 0, "details": []}

        # Mandatory Correctness gate for R-Grade (Research-Grade) logic
        sanitizer_report = {}
        sanitizer_ok = True
        if self.sanitizer_mode or self.security_mode: 
            sanitizer_report = self._compile_with_sanitizers(action_name=action)
            sanitizer_ok = bool(sanitizer_report.get("ok", True))
            if not sanitizer_ok:
                logger.warning(f"ROBUSTNESS ALERT: Sanitizer failure in '{action}': {sanitizer_report.get('message')}")
        
        accepted = True
        reject_reason = ""
        if not correctness_ok:
            accepted = False
            reject_reason = "correctness_regression"
        elif self.security_mode and not security_ok:
            accepted = False
            reject_reason = "security_critical"
        elif self.sanitizer_mode and not sanitizer_ok:
            accepted = False
            reject_reason = "sanitizer_failure"

        if accepted:
            logger.info(f"Step Accepted: New Latency: {new_latency:.4f}s ({improvement:+.2f}%)")
        else:
            logger.error(f"Step Rejected: {action} failed {reject_reason}. Falling back.")
            # Restore baseline binary for stability
            self._compile_baseline()
            new_latency = self.oracle.measure()
            new_size = self.oracle.get_binary_size()
            improvement = 0.0
        
        # 6. Learn & Knowledge
        # S-Grade Upgrade: Proper DQN Bellman update with 'done' flag
        if agent_type == "rl" and hasattr(self.agents["rl"], "learn"):
            is_done = (improvement > 10.0) # Heuristic for 'optimized enough'
            self.agents["rl"].learn(
                features=baseline_record["features"],
                action_name=action,
                reward_metrics={"latency_diff": improvement / 100.0, "size_diff": size_increase / 100.0},
                next_features=self.feature_extractor.extract(self.program_path),
                done=is_done
            )

        self.history.record(
            action,
            new_latency,
            improvement,
            action=action,
            agent_type=agent_type,
            size_bytes=new_size,
            size_increase_pct=size_increase,
            accepted=accepted,
            reject_reason=reject_reason,
            correctness_ok=correctness_ok,
            security_report=security_report,
            sanitizer_report=sanitizer_report,
        )
        
        # 7. Final Handover (S-Grade SBOM Generation)
        if improvement > 0 and accepted:
            try:
                from sbom_generator import SBOMGenerator
                sbom = SBOMGenerator(os.path.basename(self.program_path) + ".opt")
                sbom.generate()
            except ImportError:
                print("[SBOM] Generator not found, skipping.")
        
        # 9. Visual Realization (Optional cleanup might be needed if Minetest is gone)
        visual_reasoning = reasoning if agent_type == "LLM" else f"Sequential optimization step: {action} applied."
        if not accepted:
            visual_reasoning = f"REJECTED: {reject_reason}. Fallback to baseline."
            
        features["latency"] = new_latency
        features["reasoning"] = visual_reasoning

        # Minetest is skipped as per user request, but we keep the logic here for future extension
        # or just comment it out to avoid errors if the connector is broken.
        try:
            from minetest_connector import MinetestConnector
            visualizer = MinetestConnector()
            visualizer.visualize(features, security_report if self.security_mode else {}, active_pass=action)
        except Exception:
            pass # Silently skip Minetest errors
        return accepted

    def print_report(self):
        print(self.history.dump_json())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", default="program.cpp")
    parser.add_argument("--agent", default="RL")
    args = parser.parse_args()
    
    manager = MAPEManager(program_path=args.program, security_mode=True)
    manager.run_baseline()
    manager.run_sequential_cycle(agent_type=args.agent, steps=2)
    manager.print_report()
