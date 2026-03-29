import os

class Config:
    # --- Paths ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BENCHMARK_DIR = os.path.join(BASE_DIR, "benchmarks")
    
    # --- RL Hyperparameters ---
    RL_LEARNING_RATE = 0.001
    RL_DISCOUNT_FACTOR = 0.95
    RL_EPSILON_START = 1.0
    RL_EPSILON_END = 0.01
    RL_EPSILON_DECAY = 0.995
    RL_MEMORY_SIZE = 1000
    RL_BATCH_SIZE = 32
    RL_TARGET_UPDATE_FREQ = 10
    
    # --- Optimization Settings ---
    MAX_STEPS_PER_CYCLE = 5
    DEFAULT_PASSES = ["loop_unroll", "vectorize", "inline_functions", "dce", "licm", "strip"]
    
    # --- Performance Thresholds ---
    LATENCY_IMPROVEMENT_THRESHOLD = 0.01 # 1% minimum for 'good'
    SIZE_PENALTY_WEIGHT = 0.5
    
    # --- Security/Correctness ---
    ENABLE_SANITIZERS = True
    ENFORCE_CLEAN_IR = True
    GEP_OFFSET_LIMIT = 1024
    
    # --- LLM Settings ---
    OLLAMA_URL = "http://localhost:11434/api/generate"
    LLM_MODEL = "phi3"
    LLM_TIMEOUT = 30

    @staticmethod
    def setup_logging():
        import logging
        import sys
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            stream=sys.stdout
        )
        return logging.getLogger("AegisOpt")
