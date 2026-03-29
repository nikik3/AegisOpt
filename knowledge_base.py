import json

class OptimizationHistory:
    """
    The Knowledge component of MAPE-K.
    Stores the history of optimizations and their results.
    """
    def __init__(self):
        self.history = []
        self.best_record = None

    def record(self, strategy, latency, improvement, **meta):
        """
        Log an optimization attempt.
        """
        entry = {
            "strategy": strategy,
            "latency": latency,
            "improvement": improvement,
            "timestamp": len(self.history) # logical time
        }
        # Optional richer metadata (kept flexible for demos/labs)
        # Examples: action, agent_type, size_bytes, size_increase_pct, accepted, reason, security_report, correctness_ok
        for k, v in meta.items():
            entry[k] = v
        self.history.append(entry)
        
        # Update best
        if self.best_record is None or latency < self.best_record["latency"]:
            self.best_record = entry

    def get_best_strategy(self):
        if self.best_record:
            return self.best_record["strategy"]
        return "baseline"

    def get_history(self):
        return self.history
    
    def dump_json(self):
        return json.dumps(self.history, indent=2)
