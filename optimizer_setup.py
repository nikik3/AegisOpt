from agentica_lib import Agent, Environment
import os
import shutil
import subprocess
import time


def _detect_compiler() -> str | None:
    """
    Detect an available C++ compiler.
    Preference order:
      1. $CXX environment variable
      2. g++
      3. c++
      4. clang++
    Returns the compiler name or None if nothing is found.
    """
    candidates = []

    env_cxx = os.environ.get("CXX")
    if env_cxx:
        candidates.append(env_cxx)

    candidates.extend(["g++", "c++", "clang++"])

    for compiler in candidates:
        if compiler and shutil.which(compiler):
            return compiler

    return None


def llvm_opt_pass(env, pass_name):
    """
    Applies an LLVM pass using the 'opt' tool.
    Supports chaining by working on 'program_active.ll'.
    """
    base = env.program_path.replace(".cpp", "")
    active_ll = f"{base}_active.ll"
    output_ll = f"{base}_temp.ll"
    
    # 1. Ensure active IR exists
    if not os.path.exists(active_ll):
        # Generate initial IR
        clang_cmd = f"clang++ -O0 -S -emit-llvm -Xclang -disable-O0-optnone {env.program_path} -o {active_ll}"
        subprocess.run(clang_cmd, shell=True)

    if shutil.which("opt"):
        print(f"[Executor] Applying LLVM Pass: {pass_name} via 'opt'")
        opt_cmd = f"opt -S {pass_name} {active_ll} -o {output_ll}"
        try:
            subprocess.run(opt_cmd, shell=True, check=True)
            # Update active IR for the next pass in sequence
            shutil.move(output_ll, active_ll)
            # Compile current active IR to binary for measurement
            compile_cmd = f"clang++ {active_ll} -o program_opt"
            subprocess.run(compile_cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return False

def loop_unroll(env):
    print("[Executor] Applying pass: loop_unroll")
    if not llvm_opt_pass(env, "-loop-unroll"):
        compile_and_run(env, "-funroll-loops")

def inline_functions(env):
    print("[Executor] Applying pass: inline_functions")
    if not llvm_opt_pass(env, "-always-inline"):
        compile_and_run(env, "-finline-functions")

def vectorize(env):
    print("[Executor] Applying pass: vectorize")
    if not llvm_opt_pass(env, "-loop-vectorize"):
        compile_and_run(env, "-ftree-vectorize")

def dce(env):
    print("[Executor] Applying pass: dce")
    if not llvm_opt_pass(env, "-dce"):
        compile_and_run(env, "-fdce")

def licm(env):
    print("[Executor] Applying pass: licm")
    if not llvm_opt_pass(env, "-licm"):
        compile_and_run(env, "-fgcse -fgcse-lm")

def strip(env):
    print("[Executor] Applying pass: strip")
    # Strip is usually a binary level thing, not IR level
    compile_and_run(env, "-s")

def compile_and_run(env, flags):
    """
    Helper to compile and run the program with specific flags
    """
    compiler = _detect_compiler()
    if compiler is None:
        print("[Executor] Error: No suitable C++ compiler found.")
        print("           Please install `g++` or `clang++` (e.g., `sudo apt install g++`)")
        return

    cmd = f"{compiler} -O3 {flags} {env.program_path} -o program_opt"
    print(f"[Executor] Compiling: {cmd}")
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        
        print(f"[Executor] Running optimized program...")
        start_time = time.time()
        result = subprocess.run("./program_opt", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        
        execution_time = end_time - start_time
        for line in result.stdout.split('\n'):
            if "Execution time:" in line:
                print(f"[Executor] {line}")
        
        print(f"[Executor] Total System Time: {execution_time:.4f} sec")
        
    except FileNotFoundError as e:
        print(f"[Executor] Compilation failed (compiler not found): {e}")
    except subprocess.CalledProcessError as e:
        print(f"[Executor] Compilation or Execution failed: {e}")

def setup_environment(program_path="program.cpp"):
    env = Environment(program_path)
    
    agent = Agent("Optimizer")
    agent.connect(env)
    # Register tools
    agent.register_tool("loop_unroll", loop_unroll)
    agent.register_tool("inline_functions", inline_functions)
    agent.register_tool("vectorize", vectorize)
    agent.register_tool("dce", dce)
    agent.register_tool("licm", licm)
    agent.register_tool("strip", strip)
    
    return agent, env
