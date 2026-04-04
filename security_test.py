from security_agent import SecurityAgent
agent = SecurityAgent()
result = agent.analyze_source_code("cli_test/vulnerable_demo.cpp")
print(result)
