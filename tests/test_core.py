import pytest
import numpy as np
import os
from rl_agent import DQNAgent
from security_agent import SecurityAgent
from ml_cost_model import MLCostModel
from config import Config

def test_dqn_initialization():
    agent = DQNAgent(action_space=["a1", "a2"], state_dim=10)
    assert agent.w1.shape == (10, 16)
    assert agent.w2.shape == (16, 2)
    assert agent.epsilon == Config.RL_EPSILON_START

def test_dqn_choose_action():
    agent = DQNAgent(action_space=["loop_unroll"], state_dim=10)
    features = {"bb_count": 10}
    action = agent.choose_action(features)
    assert action == "loop_unroll"

def test_security_scan_owasp():
    agent = SecurityAgent()
    # Create a dummy IR file with a dangerous call
    dummy_ir = "call void @gets(i8* null)"
    with open("test.ll", "w") as f:
        f.write(dummy_ir)
    
    report = agent.scan_ir("test.ll")
    assert report["issues_found"] > 0
    assert any("gets" in d["item"] for d in report["details"])
    os.remove("test.ll")

def test_ml_cost_model_prediction():
    model = MLCostModel()
    features = {"arithmetic_ratio": 0.8, "mem_ops_ratio": 0.2}
    latency = model.predict_latency(features, ["vectorize"])
    assert latency > 0
    assert isinstance(latency, float)

def test_config_integrity():
    assert Config.RL_LEARNING_RATE > 0
    assert os.path.isabs(Config.BASE_DIR)
