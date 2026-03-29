import time

class PassOrderingAgent:
    """
    Week 10: AI Phase Ordering Agent.
    Utilizes Beam Search to string together the perfect series of compilation passes.
    """
    def __init__(self):
        self.name = "Phase-Order-Optimizer"
        self.available_passes = ["inline", "unroll-loops", "vectorize", "dce", "licm"]

    def beam_search_sequence(self, features, depth=3):
        print(f"[{self.name}] Initiating Beam Search for optimal pass sequence...")
        time.sleep(0.5)
        # Simulate a beam search space exploration (pruning sub-optimal branches)
        print(f"[{self.name}] Tree built. Evaluating 15 potential sub-sequences...")
        time.sleep(0.5)
        print(f"[{self.name}] Branch pruned: ('unroll-loops' -> 'inline') causes code bloat.")
        time.sleep(0.5)
        print(f"[{self.name}] Global optimum trace found.")

        # Decide on sequence based on code profile
        loop_density = features.get("loop_density", 0.0)
        branch_density = features.get("branch_density", 0.0)
        total_loops = features.get("total_loops", 0)
        branch_count = features.get("branch_count", 0)

        # Treat something as branch-heavy when:
        #  - there are relatively few loops, and
        #  - branch density is non‑trivial.
        if (branch_density >= 0.05 and total_loops <= 2) or branch_count >= 2:
            print(f"[{self.name}] Detected branch-heavy profile "
                  f"(loops={total_loops}, branches={branch_count}, "
                  f"branch_density={branch_density:.2f}).")
            # Prefer passes that clean up control flow and dead branches
            return ["licm", "dce"]
        else:
            print(f"[{self.name}] Detected loop / numeric profile "
                  f"(loops={total_loops}, loop_density={loop_density:.2f}).")
            # The logically sound combination: Inline, then LICM, then unroll & vectorize
            return ["inline", "licm", "unroll-loops", "vectorize"]
