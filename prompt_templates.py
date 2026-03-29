SYSTEM_PROMPT = """
You are an expert compiler optimization engineer.
Your goal is to analyze C++ source code and suggest the single best optimization pass.
Output format: JSON { "pass": "name", "reason": "explanation" }
"""

ANALYSIS_PROMPT = """
Analyze the following code for performance bottlenecks:
{code}
"""
