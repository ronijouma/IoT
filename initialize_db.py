import sqlite3

# SQLite-konfiguration
DB_FILE = "sensor_data.db"

def create_table():
    """Skapar tabellen för sensordata om den inte redan finns."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        device_id TEXT,
        temperature REAL,
        humidity REAL
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Tabellen 'sensor_data' är skapad!")