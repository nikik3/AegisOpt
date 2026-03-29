from agentica_lib import Agent
import json

class RuleBasedAgent(Agent):
    """
    Week 5: The Intelligent Orchestrator.
    Uses Heuristic-Based Logic to select optimizations.
    """
    def __init__(self, name="AegisOpt Agent", goal="performance"):
        super().__init__(name)
        self.goal = goal # performance or size

    def act(self):
        """
        Decision Engine: Maps Features -> Rules -> Actions.
        """
        features = self.observation
        print(f"\n[Agent] Thinking... (Goal: {self.goal})")
        
        # --- Heuristics / Rules Engine ---
        
        # Rule C: Size Constraint
        if self.goal == "size":
            explanation = "Goal is 'size'. Minimizing binary footprint."
            action = "strip"
            self.explain_decision("Size Constraint", explanation, action)
            return self.execute_action(action)

        # Rule A: Loop Heavy
        # If loop density is high (> 0.1 loops per instruction)
        loop_density = features.get("loop_density", 0)
        total_loops = features.get("total_loops", 0)
        
        if loop_density > 0.05 or total_loops > 2:
            explanation = f"Detected high loop density ({loop_density:.2f}) or Count ({total_loops}). Unrolling helps ILP."
            action = "loop_unroll"
            self.explain_decision("Loop Heavy", explanation, action)
            return self.execute_action(action)

        # Rule B: Memory Heavy
        # If load/store count is high
        load_store = features.get("load_store_count", 0)
        instruction_count = features.get("instruction_count", 1)
        
        if load_store / instruction_count > 0.3:
             explanation = f"High memory traffic detected ({load_store} ops). LICM helps reduce redundant access."
             action = "licm"
             self.explain_decision("Memory Heavy", explanation, action)
             return self.execute_action(action)

        # Fallback / Default
        explanation = "No specific dominant feature detected. Applying standard vectorization."
        action = "vectorize"
        self.explain_decision("Default", explanation, action)
        return self.execute_action(action)

    def explain_decision(self, rule_name, reasoning, action):
        """
        The 'Heuristic Explainer' for S-Grade Traceability.
        """
        print(f"[Agent] Rule Triggered: [{rule_name}]")
        print(f"[Agent] Reasoning: \"{reasoning}\"")
        print(f"[Agent] Decision: Apply Pass '{action}'")

    def execute_action(self, action):
        return action
