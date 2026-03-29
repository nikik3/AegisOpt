import os
import sys
# Add parent directory to path to allow importing feature_extractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feature_extractor import extract_features
import json

def run_demo():
    print("=== Phase 1: LLVM IR Feature Extraction ===")
    test_file = "program.cpp"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("int main() { int a=0; for(int i=0; i<100; i++) a+=i; return a; }")
    
    features = extract_features(test_file)
    print(f"\n[Success] Extracted raw IR features for {test_file}:")
    print(json.dumps(features, indent=4))
    print("\nMotivation: To provide 'sight' to our AI agents by converting code into numeric vectors.")

if __name__ == "__main__":
    run_demo()
