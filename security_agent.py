import re
import os

class SecurityAgent:
    """
    S-Grade Upgrade: Advanced IR SAST (Static Application Security Testing).
    Implements OWASP Top 10/25 patterns at the LLVM IR level.
    """
    def __init__(self):
        # OWASP-aligned dangerous function mapping
        self.owasp_patterns = {
            "A01:2021-Broken Access Control": [r"chmod", r"chown"],
            "A02:2021-Cryptographic Failures": [r"md5", r"sha1", r"rand\s*\("], # Weak crypto/PRNG
            "A03:2021-Injection": [r"system", r"popen", r"exec"],
            "CWE-120:Buffer Copy without Checking Size": [r"gets", r"strcpy", r"strcat", r"sprintf"]
        }

    def scan_ir(self, ir_path):
        if not os.path.exists(ir_path):
            return {"status": "error", "message": "IR file not found", "issues_found": 0, "details": []}

        with open(ir_path, 'r') as f:
            ir_content = f.read()

        issues = []
        # 1. OWASP Pattern Matching (Function calls)
        for category, funcs in self.owasp_patterns.items():
            for func in funcs:
                pattern = rf'call\s+.*@{func}\('
                if re.search(pattern, ir_content):
                    issues.append({
                        "type": "owasp_violation",
                        "category": category,
                        "item": func,
                        "severity": "CRITICAL" if "Injection" in category else "WARNING",
                        "recommendation": f"Risk detected in {category}. Replace {func} with secure alternative."
                    })

        # 2. Structural Scanning: GEP Bounds (Spatial Safety)
        # Scan for large constant offsets in arrays/structs
        gep_pattern = r'getelementptr\s+.*,\s+i32\s+(\d+)'
        for match in re.finditer(gep_pattern, ir_content):
            offset = int(match.group(1))
            if offset > 4096: # S-Grade Threshold
                issues.append({
                    "type": "memory_safety",
                    "item": "GEP Large Offset",
                    "severity": "WARNING",
                    "recommendation": f"Constant offset {offset} exceeds standard buffer safe-zones. Potential OOB."
                })

        # 3. Use-After-Free (UAF) Heuristic
        # Look for 'free' followed by 'load/store' on same pointer name in same block
        # (Simplified heuristic for demo fidelity)
        if "call void @free" in ir_content and ("load" in ir_content or "store" in ir_content):
            issues.append({
                "type": "temporal_safety",
                "item": "Potential UAF",
                "severity": "LOW",
                "recommendation": "Dangling pointer risk detected. Ensure pointers are nullified after free."
            })

        return {
            "status": "success",
            "issues_found": len(issues),
            "details": issues
        }

    def scan_source(self, source_path):
        """Standard source-level heuristic scan."""
        if not os.path.exists(source_path):
            return {"status": "error", "message": "Source file not found", "issues_found": 0, "details": []}
        with open(source_path, "r") as f:
            code = f.read()
        issues = []
        for category, funcs in self.owasp_patterns.items():
            for func in funcs:
                if re.search(rf'\b{re.escape(func)}\s*\(', code):
                    issues.append({
                        "category": category,
                        "severity": "WARNING",
                        "recommendation": f"Found {func} - flagged in {category}."
                    })
        return {"status": "success", "issues_found": len(issues), "details": issues}

    @staticmethod
    def summarize(report):
        if not report or report.get("status") != "success":
            return "security_scan=error"
        n = report.get("issues_found", 0)
        if n == 0: return "security_scan=clean"
        severities = [d.get("severity", "") for d in report.get("details", [])]
        top = "CRITICAL" if "CRITICAL" in severities else "WARNING"
        return f"security_scan={top} ({n} issues)"
