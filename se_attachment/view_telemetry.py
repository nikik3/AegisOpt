import sqlite3
import pandas as pd
import os

def view_telemetry():
    db_path = os.path.join(os.path.dirname(__file__), "hft_telemetry.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found. Run a simulation first.")
        return

    try:
        conn = sqlite3.connect(db_path)
        # We use pandas just to print it nicely, but raw sqlite works too
        query = "SELECT timestamp, kernel_name, agent_type, pass_sequence, latency_improvement_percent FROM compilation_metrics"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("Database is empty. No telemetry recorded yet.")
        else:
            print("\n=== AegisOpt HFT Telemetry Database ===")
            print(df.to_string(index=False))
            print("=======================================\n")
            
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    view_telemetry()
