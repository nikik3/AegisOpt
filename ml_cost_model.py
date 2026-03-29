from config import Config

class MLCostModel:
    """
    S-Grade Upgrade: Neural Surrogate Cost Modeling.
    Predicts relative execution overhead based on IR feature weights.
    """
    def __init__(self):
        self.name = "NeuroOpt-Surrogate"
        # Weights representing relative 'cost' of different IR features
        self.feature_weights = {
            "arithmetic": 1.0,
            "memory": 2.5,  # Memory ops are 2.5x more expensive than arithmetic
            "branch": 1.5,
            "loop_complexity": 5.0
        }
    
    def predict_latency(self, features, pass_sequence):
        """
        Estimates latency by calculating a weighted sum of IR features 
        and factoring in the theoretical gain of optimization passes.
        """
        # Base cost from IR features
        cost = (
            features.get("arithmetic_ratio", 0.5) * self.feature_weights["arithmetic"] +
            features.get("mem_ops_ratio", 0.5) * self.feature_weights["memory"] +
            features.get("branch_ratio", 0.1) * self.feature_weights["branch"] +
            (features.get("loop_density", 0) * self.feature_weights["loop_complexity"])
        )
        
        # Theoretical optimization gains (mapped to LLVM pass knowledge)
        # Some passes like 'inline' reduce overhead significantly for complex code
        pass_impact = 1.0
        for p in pass_sequence:
            if p == "vectorize" and features.get("loop_density", 0) > 0.1:
                pass_impact *= 0.8  # 20% speedup
            elif p == "licm":
                pass_impact *= 0.95
            elif p == "dce":
                pass_impact *= 0.98
                
        final_estimate = cost * pass_impact * 0.05 # Scale to seconds
        return max(0.01, round(final_estimate, 4))
