import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security_agent import SecurityAgent

def run_demo():
    print("=== Week 9 Demo: Security SAST & Robustness Radar ===")
    
    vulnerable_ir = "test_vuln.ll"
    with open(vulnerable_ir, "w") as f:
        f.write("call void @gets(i8* null) ; OWASP Violation\n")
        f.write("%ptr = getelementptr i32, i32* %base, i32 5000 ; Large Offset Risk\n")
    
    agent = SecurityAgent()
    report = agent.scan_ir(vulnerable_ir)
    summary = agent.summarize(report)
    
    print(f"\n[Security Radar] Static Analysis Result: {summary}")
    for issue in report["details"]:
        print(f"  - [{issue['severity']}] {issue['category'] if 'category' in issue else issue['type']}: {issue['recommendation']}")
    
    print("\nLogic: Any step causing a security violation index > threshold is automatically ROLLBACKED.")
    os.remove(vulnerable_ir)

if __name__ == "__main__":
    run_demo()
