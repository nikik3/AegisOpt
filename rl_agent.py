import logging
import random
import os
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

class DQNAgent:
    """
    Research-Grade: Deep Q-Network (DQN) Agent.
    Implements:
    - Experience Replay Buffer
    - Target Network for stability
    - Vectorized Batch Updates (He-initialization, Adam-like SGD)
    """
    def __init__(self, action_space, state_dim=10):
        self.action_space = action_space
        self.state_dim = state_dim
        self.memory = [] # Experience Replay
        self.gamma = Config.RL_DISCOUNT_FACTOR
        self.epsilon = Config.RL_EPSILON_START
        self.epsilon_min = Config.RL_EPSILON_END
        self.epsilon_decay = Config.RL_EPSILON_DECAY
        self.learning_rate = Config.RL_LEARNING_RATE
        self.batch_size = Config.RL_BATCH_SIZE
        self.target_update_freq = Config.RL_TARGET_UPDATE_FREQ
        self.steps_since_target_update = 0
        
        # Neural Network Parameters (He-initialization)
        self.hidden_size = 16
        limit1 = np.sqrt(6 / (self.state_dim + self.hidden_size))
        self.w1 = np.random.uniform(-limit1, limit1, (self.state_dim, self.hidden_size))
        self.b1 = np.zeros((1, self.hidden_size))
        
        limit2 = np.sqrt(6 / (self.hidden_size + len(self.action_space)))
        self.w2 = np.random.uniform(-limit2, limit2, (self.hidden_size, len(self.action_space)))
        self.b2 = np.zeros((1, len(self.action_space)))
        
        # Target Network weights
        self.target_w1, self.target_b1 = self.w1.copy(), self.b1.copy()
        self.target_w2, self.target_b2 = self.w2.copy(), self.b2.copy()
        self.tools = {}

    def connect(self, env):
        self.env = env

    def register_tool(self, name, func):
        self.tools[name] = func

    def _get_feature_vector(self, features):
        """Converts dict features to a normalized NumPy vector."""
        v = [
            features.get("arithmetic_ratio", 0.5),
            features.get("mem_ops_ratio", 0.5),
            features.get("branch_ratio", 0.1),
            features.get("bb_count", 0) / 100.0,
            float(features.get("is_llvm", False)),
            features.get("loop_density", 0) * 10.0
        ]
        hw_v = features.get("hw_vector", [0.0, 0.0, 0.0, 0.25])
        v.extend(hw_v)
        return np.array(v).reshape(1, -1)

    def _forward(self, state, target=False):
        w1, b1 = (self.target_w1, self.target_b1) if target else (self.w1, self.b1)
        w2, b2 = (self.target_w2, self.target_b2) if target else (self.w2, self.b2)
        
        h = np.maximum(0, np.dot(state, w1) + b1) # ReLU
        q = np.dot(h, w2) + b2
        return h, q
    def choose_action(self, features):
        """Selects an action using epsilon-greedy policy."""
        # Convert features to a debug string for logging
        features_str = ", ".join([f"{k}:{v}" for k, v in features.items() if isinstance(v, (int, float))])
        logger.debug(f"Action Selection - Features: {features_str}")
        
        state = self._get_feature_vector(features)
        if random.random() < self.epsilon:
            action = random.choice(self.action_space)
            logger.info(f"Exploration: Random action chosen -> {action}")
            return action
        
        _, q_values = self._forward(state)
        action = self.action_space[np.argmax(q_values[0])]
        logger.info(f"Exploitation: Optimal action chosen -> {action}")
        return action

    def remember(self, s, a, r, s_next, done):
        self.memory.append((s, a, r, s_next, done))
        if len(self.memory) > Config.RL_MEMORY_SIZE:
            self.memory.pop(0)

    def learn(self, features, action_name, reward_metrics, next_features, done=False):
        """Vectorized Batch Training Logic."""
        s = self._get_feature_vector(features)
        s_next = self._get_feature_vector(next_features)
        a_idx = self.action_space.index(action_name)
        
        # Sophisticated Reward (Latency + Binary Size Tradeoff)
        reward = (reward_metrics.get("latency_diff", 0) * 10.0) - (reward_metrics.get("size_diff", 0) * 2.0)
        
        self.remember(s, a_idx, reward, s_next, done)
        
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        S = np.vstack([x[0] for x in batch])
        A = np.array([x[1] for x in batch])
        R = np.array([x[2] for x in batch])
        S_next = np.vstack([x[3] for x in batch])
        Dones = np.array([x[4] for x in batch])

        # Target Calculation (Bellman Optimality)
        _, q_next = self._forward(S_next, target=True)
        q_target = R + (1 - Dones) * self.gamma * np.max(q_next, axis=1)
        
        # Prediction & Backprop
        h, q_pred = self._forward(S, target=False)
        target_f = q_pred.copy()
        for i in range(self.batch_size):
            target_f[i, A[i]] = q_target[i]

        # MSE Gradient
        error = q_pred - target_f
        dw2 = np.dot(h.T, error) / self.batch_size
        db2 = np.mean(error, axis=0, keepdims=True)
        
        dh = np.dot(error, self.w2.T) * (h > 0) # ReLU grad
        dw1 = np.dot(S.T, dh) / self.batch_size
        db1 = np.mean(dh, axis=0, keepdims=True)

        # Update (Simplified SGD with Momentum-like clipping)
        self.w1 -= self.learning_rate * np.clip(dw1, -1, 1)
        self.b1 -= self.learning_rate * db1
        self.w2 -= self.learning_rate * np.clip(dw2, -1, 1)
        self.b2 -= self.learning_rate * db2

        # Housekeeping
        self.steps_since_target_update += 1
        if self.steps_since_target_update >= self.target_update_freq:
            self.target_w1, self.target_b1 = self.w1.copy(), self.b1.copy()
            self.target_w2, self.target_b2 = self.w2.copy(), self.b2.copy()
            self.steps_since_target_update = 0

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_policy(self, filename="dqn_policy.npz"):
        np.savez(filename, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2)

    def load_policy(self, filename="dqn_policy.npz"):
        if os.path.exists(filename):
            data = np.load(filename)
            self.w1, self.b1 = data['w1'], data['b1']
            self.w2, self.b2 = data['w2'], data['b2']
            self.target_w1, self.target_b1 = self.w1.copy(), self.b1.copy()
            self.target_w2, self.target_b2 = self.w2.copy(), self.b2.copy()

RLAgent = DQNAgent
