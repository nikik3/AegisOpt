import re
import os
import subprocess
import shutil
from hardware_profiler import HardwareProfiler

def extract_features_llvm(file_path):
    """
    Analyzes LLVM IR to extract high-fidelity features.
    
    Args:
        file_path (str): Path to the C++ source file.
    """
    temp_ll = file_path.replace(".cpp", ".ll")
    
    # 1. Generate LLVM IR
    # Use clang++ for C++ files to properly resolve standard headers (<chrono>, etc.)
    clang_cmd = f"clang++ -O0 -S -emit-llvm -Xclang -disable-O0-optnone {file_path} -o {temp_ll}"
    try:
        subprocess.run(clang_cmd, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"[FeatureExtractor] Error generating LLVM IR: {e}")
        return None

    if not os.path.exists(temp_ll):
        return None

    with open(temp_ll, 'r') as f:
        ir_content = f.read()

    # 2. Extract Features from IR
    # LLVM IR is much more predictable than source code.
    
    # Instruction Mix
    arithmetic_instrs = len(re.findall(r'\b(add|sub|mul|sdiv|udiv|fadd|fsub|fmul|fdiv)\b', ir_content))
    load_instrs = len(re.findall(r'\bload\b', ir_content))
    store_instrs = len(re.findall(r'\bstore\b', ir_content))
    call_instrs = len(re.findall(r'\bcall\b', ir_content))
    branch_instrs = len(re.findall(r'\bbr\b', ir_content))
    
    total_instrs = arithmetic_instrs + load_instrs + store_instrs + call_instrs + branch_instrs
    
    # Block & Function structure
    basic_blocks = len(re.findall(r'; <label>:', ir_content)) + len(re.findall(r'^\w+:', ir_content, re.MULTILINE))
    functions = len(re.findall(r'^define\b', ir_content, re.MULTILINE))

    # Loop detection (Heuristic: search for back-edges or "loop" metadata)
    # For a simple heuristic, we count branch instructions that go to an earlier label
    # but that's complex to parse with regex. We'll use a simpler 'phi' count as a proxy for loop/merge nodes.
    phi_nodes = len(re.findall(r'\bphi \b', ir_content))

    features = {
        "llvm_instr_count": total_instrs,
        "arithmetic_ratio": arithmetic_instrs / total_instrs if total_instrs > 0 else 0,
        "mem_ops_ratio": (load_instrs + store_instrs) / total_instrs if total_instrs > 0 else 0,
        "branch_ratio": branch_instrs / total_instrs if total_instrs > 0 else 0,
        "bb_count": basic_blocks,
        "func_count": functions,
        "loop_proxy_score": phi_nodes,
        "is_llvm": True
    }
    
    # Cleanup
    # os.remove(temp_ll) # Keep for debugging if needed
    
    return features

def extract_features(file_path):
    """
    Analyzes code to extract features, preferring LLVM IR if clang is available.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # Attempt LLVM Extraction first (DISABLED for this environment because
    # clang++ standard C++ headers are not fully configured and spam errors).
    # Regex-based extraction is sufficient for the current demos/evaluation.
    #
    # If you later fix clang's C++ headers, you can re‑enable this block.
    # --- SCIENTIFIC S-GRADE: Sequential State Tracking ---
    # In Phase Ordering, we must analyze the IR *after* each pass.
    base = file_path.replace(".cpp", "")
    active_ll = f"{base}_active.ll"
    
    if os.path.exists(active_ll) and shutil.which("clang++"):
        print(f"[FeatureExtractor] Analyzing ACTIVE IR for state tracking: {active_ll}")
        with open(active_ll, 'r') as f:
            ir_content = f.read()
        
        # Extraction logic mirroring the internal extract_features_llvm
        arithmetic_instrs = len(re.findall(r'\b(add|sub|mul|sdiv|udiv|fadd|fsub|fmul|fdiv)\b', ir_content))
        load_instrs = len(re.findall(r'\bload\b', ir_content))
        store_instrs = len(re.findall(r'\bstore\b', ir_content))
        total_instrs = max(1, arithmetic_instrs + load_instrs + store_instrs)
        
        llvm_features = {
            "instruction_count": total_instrs,
            "arithmetic_ratio": arithmetic_instrs / total_instrs,
            "mem_ops_ratio": (load_instrs + store_instrs) / total_instrs,
            "bb_count": len(re.findall(r'; <label>:', ir_content)) + 1,
            "is_llvm": True,
            "memory_bound": (load_instrs + store_instrs) / total_instrs > 0.4
        }
        return llvm_features

    # Standard LLVM Extraction for fresh files
    if shutil.which("clang++"):
        llvm_features = extract_features_llvm(file_path)
        if llvm_features:
            # Add some legacy fields to avoid breaking downstream agents
            llvm_features["instruction_count"] = llvm_features["llvm_instr_count"]
            llvm_features["loop_density"] = llvm_features["loop_proxy_score"] / llvm_features["llvm_instr_count"] if llvm_features["llvm_instr_count"] > 0 else 0
            # Ensure the structure matches what rule-based/RL agents expect
            llvm_features["total_loops"] = llvm_features.get("loop_proxy_score", 0)
            llvm_features["load_store_count"] = int(llvm_features["mem_ops_ratio"] * llvm_features["llvm_instr_count"])
            llvm_features["memory_bound"] = llvm_features["mem_ops_ratio"] > 0.4
            print(f"[FeatureExtractor] LLVM Analysis Success: {file_path}")
            return llvm_features

    # Fallback to Regex (Legacy)
    print(f"[FeatureExtractor] Falling back to Regex for {file_path}")
    with open(file_path, 'r') as f:
        code = f.read()

    instruction_count = 0
    clean_lines = []
    for line in code.split('\n'):
        line = line.strip()
        if line and not line.startswith('//') and not line.startswith('#'):
            instruction_count += 1
            clean_lines.append(line)
    
    clean_code = '\n'.join(clean_lines)

    for_loops = len(re.findall(r'\bfor\s*\(', clean_code))
    while_loops = len(re.findall(r'\bwhile\s*\(', clean_code))
    total_loops = for_loops + while_loops

    if_stmts = len(re.findall(r'\bif\s*\(', clean_code))
    switch_stmts = len(re.findall(r'\bswitch\s*\(', clean_code))
    ternary_ops = len(re.findall(r'\?', clean_code))
    branch_count = if_stmts + switch_stmts + ternary_ops

    assignments = len(re.findall(r'=[^=]', clean_code)) 
    array_accesses = len(re.findall(r'\[.*?\]', clean_code))
    load_store_count = assignments + array_accesses

    function_pattern = r'\b(void|int|double|float|bool|auto)\s+\w+\s*\([^)]*\)\s*\{'
    functions = len(re.findall(function_pattern, clean_code))
    
    loop_density = total_loops / instruction_count if instruction_count > 0 else 0
    branch_density = branch_count / instruction_count if instruction_count > 0 else 0

    features = {
        "instruction_count": instruction_count,
        "total_loops": total_loops,
        "loop_density": loop_density,
        "branch_count": branch_count,
        "branch_density": branch_density,
        "load_store_count": load_store_count,
        "functions": functions,
        "loops": total_loops,
        "memory_accesses": array_accesses, 
        "memory_bound": (load_store_count > instruction_count * 0.3),
        "is_llvm": False
    }
    
    return features

if __name__ == "__main__":
    print(extract_features("program.cpp"))
