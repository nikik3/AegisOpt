#!/bin/bash

echo "=============================================="
echo "   AEGISOPT: AGENTIC COMPILER SYSTEM v2.0"
echo "=============================================="
echo "1. Initializing Workspaces & Feature Extractors..."
python3 optimizer_setup.py

echo ""
echo "2. Activating Intelligent Agents..."
echo " > [Agent] RL Constraint Solver: ONLINE"
echo " > [Agent] LLM Strategist: ONLINE"
echo " > [Agent] Dynamic Profiler: ONLINE"
echo " > [Agent] Surrogate Cost Modeler: ONLINE"

echo "----------------------------------------------"
echo "System Environment Ready. Executing Full Test Suite..."
echo "----------------------------------------------"
sleep 1

# Professional Run (Weeks 8 - 14)
echo -e "\n--- WEEK 8 MODULE ---\n"
python3 week8_demo.py

echo -e "\n--- WEEK 9 MODULE ---\n"
python3 week9_demo.py

echo -e "\n--- WEEK 10 MODULE ---\n"
python3 week10_demo.py

echo -e "\n--- WEEK 11 MODULE ---\n"
python3 week11_demo.py

echo -e "\n--- WEEK 12 MODULE ---\n"
python3 week12_demo.py

echo -e "\n--- WEEK 13 MODULE ---\n"
python3 week13_demo.py

echo -e "\n--- FINAL INTEGRATION ---\n"
python3 week14_demo.py
