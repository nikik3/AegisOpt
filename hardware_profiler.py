import subprocess
import os

class HardwareProfiler:
    """
    SCIENTIFIC S-GRADE: Detects target-specific hardware features.
    Allows the AI agent to be 'Hardware Aware'.
    """
    def __init__(self):
        self.features = self._detect_features()

    def _detect_features(self):
        features = {
            "has_avx": False,
            "has_sse4": False,
            "has_neon": False, # For ARM
            "cpu_cores": os.cpu_count() or 1
        }
        
        try:
            # Check for x86 flags
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read().lower()
                    if "avx" in content: features["has_avx"] = True
                    if "sse4" in content: features["has_sse4"] = True
            
            # Check for ARM neon
            lscpu = subprocess.check_output("lscpu", shell=True).decode().lower()
            if "neon" in lscpu or "asimd" in lscpu:
                features["has_neon"] = True
                
        except Exception:
            pass # Fallback to False
            
        return features

    def get_feature_vector(self):
        """Returns a binary vector of hardware capabilities."""
        return [
            1.0 if self.features["has_avx"] else 0.0,
            1.0 if self.features["has_sse4"] else 0.0,
            1.0 if self.features["has_neon"] else 0.0,
            self.features["cpu_cores"] / 16.0 # Normalized core count
        ]

if __name__ == "__main__":
    hp = HardwareProfiler()
    print(f"Hardware Detected: {hp.features}")
