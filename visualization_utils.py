from analytics_engine import AnalyticsEngine

def generate_radar_chart(dna_data):
    """
    Week 13: Visualization Utility.
    Generates ASCII or JSON data for a Radar Chart.
    """
    print("--- Analytics: Code DNA Radar ---")
    for key, value in dna_data.items():
        bar_len = int(value * 20)
        bar = "#" * bar_len
        print(f"{key:<20} | {bar:<20} ({value:.2f})")

def main():
    engine = AnalyticsEngine()
    features = {"loop_density": 0.4, "branch_density": 0.1, "memory_bound": True}
    
    dna = engine.compute_code_dna(features)
    generate_radar_chart(dna)

if __name__ == "__main__":
    main()
