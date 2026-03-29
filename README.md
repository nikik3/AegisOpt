# AegisOpt 🛡️ 

**Agentic AI-Driven Compiler Optimization Framework**

AegisOpt is a multi-agent AI system that sits on top of standard compilers (like GCC and LLVM). Instead of relying on static, one-size-fits-all optimization flags like `-O3`, AegisOpt uses **Reinforcement Learning** to dynamically discover the absolute best sequence of compiler passes for your specific source code and hardware.

It also integrates a strict **Security Radar** to ensure the AI doesn't introduce vulnerabilities during optimization.

---

## 🚀 Features

*   **Deep Q-Network (RL) Optimizer**: Explores thousands of compiler pass combinations to find the fastest execution sequence.
*   **Security Radar (SAST)**: Automatically scans Intermediate Representation (IR) to veto unsafe optimizations.
*   **Live Web Dashboard**: A Flask-based interactive UI that lets you visualize the AI's decision-making process in real-time.
*   **Hardware Profiler**: Detects your specific CPU architecture (AVX/SSE) to tailor optimizations to your silicon.
*   **SE Fintech Attachment**: Includes a completely separable domain module for High-Frequency Trading telemetry logging (using SQLite).

---

## 📦 Installation

**Prerequisites**: 
You must have `python3`, `g++`, and `llvm` installed on your Linux environment.

1. Clone the repository and enter the directory:
   ```bash
   cd aegisopt
   ```
2. Set up a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Running the Project

### 1. The Interactive Presentation Dashboard 
This starts a local web server where you can run the entire pipeline visually.
```bash
python3 dashboard_app.py
```
*   Open your browser and navigate to `http://localhost:8000`
*   Click through the terminal buttons to see the AI analyze features, optimize the code, and run security checks.



---

## 🏗 System Architecture (MAPE-K)

AegisOpt is built on the **Monitor-Analyze-Plan-Execute (MAPE)** loop:
1. **Monitor**: Parses the C++ into LLVM IR and records baseline execution latency.
2. **Analyze**: The `FeatureExtractor` turns the IR into a mathematical state vector.
3. **Plan**: The `RLAgent` predicts the Q-values of different actions (`dce`, `inline`, `vectorize`).
4. **Execute**: The compiler runs the selected passes, checks it against the `SecurityAgent`, and returns the new latency as a reward for the ML model.
