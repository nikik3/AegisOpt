import subprocess
import time
import statistics
import os

class PerformanceOracle:
    """
    The Monitor component of MAPE-K.
    Accurately measures the performance (latency) of a compiled binary.
    """
    def __init__(self, binary_path="./program_opt"):
        self.binary_path = binary_path

    def get_binary_size(self):
        """
        Returns the size of the binary in bytes.
        """
        if os.path.exists(self.binary_path):
            return os.path.getsize(self.binary_path)
        return float('inf')

    def get_output(self):
        """
        Runs the binary and returns the stdout for functional verification.
        """
        if not os.path.exists(self.binary_path):
            return ""
        try:
            result = subprocess.run(self.binary_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            out = result.stdout.strip()
            # Many of our demo benchmarks print timing; strip those lines so "golden output"
            # checks compare functional output, not performance noise.
            filtered_lines = []
            for line in out.splitlines():
                if "Execution time" in line:
                    continue
                filtered_lines.append(line.rstrip())
            return "\n".join(filtered_lines).strip()
        except:
            return "ERROR_EXECUTION"

    def measure(self, iterations=3):
        """
        Runs the binary multiple times and returns the mean latency.
        """
        if not os.path.exists(self.binary_path):
            print(f"[Oracle] Error: Binary '{self.binary_path}' not found.")
            return float('inf')

        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                subprocess.run(self.binary_path, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                end = time.perf_counter()
                latencies.append(end - start)
            except subprocess.CalledProcessError:
                print(f"[Oracle] Execution failed during measurement.")
                return float('inf')

        mean_latency = statistics.mean(latencies)
        return mean_latency
