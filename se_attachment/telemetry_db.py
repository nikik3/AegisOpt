import sqlite3
import datetime

class TelemetryDBMS:
    """
    SE Project Requirement: Integration of DBMS capabilities for telemetry management.
    Stores agent optimization feedback loops and latency drops for financial computing workloads.
    """
    def __init__(self, db_path="optimization_telemetry.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_schema()

    def _init_schema(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS compilation_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                kernel_name TEXT,
                agent_type TEXT,
                pass_sequence TEXT,
                baseline_latency REAL,
                optimized_latency REAL,
                latency_improvement_percent REAL,
                security_passed BOOLEAN
            )
        ''')
        self.conn.commit()

    def log_optimization(self, kernel, agent, passes, baseline, optimized, sec_passed):
        improvement = ((baseline - optimized) / baseline) * 100 if baseline > 0 else 0
        
        self.cursor.execute('''
            INSERT INTO compilation_metrics 
            (timestamp, kernel_name, agent_type, pass_sequence, baseline_latency, optimized_latency, latency_improvement_percent, security_passed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.now().isoformat(),
            kernel,
            agent,
            passes,
            baseline,
            optimized,
            improvement,
            sec_passed
        ))
        self.conn.commit()
        print(f"[DBMS Telemetry] Logged {improvement:.2f}% micro-latency improvement for {kernel} to SQLite.")

    def get_all_records(self):
        self.cursor.execute('SELECT * FROM compilation_metrics')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = TelemetryDBMS()
    print("[DBMS Telemetry] Database initialized successfully.")
    db.close()
