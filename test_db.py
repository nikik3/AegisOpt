import sqlite3, os
db_path = os.path.join(os.getcwd(), "hft_telemetry.db")
print("Path:", db_path)
print("Exists:", os.path.exists(db_path))
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, latency_improvement_percent, pass_sequence FROM compilation_metrics ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()
    print("Rows:", rows)
