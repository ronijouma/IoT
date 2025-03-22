import sqlite3
import pandas as pd

# Anslut till SQLite-databasen
conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()

def create_table():
    """Skapar tabellen för sensor-data om den inte redan finns."""
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

def insert_data(timestamp, device_id, temperature, humidity):
    """Lägger till data i databasen."""
    cursor.execute("""
    INSERT INTO sensor_data (timestamp, device_id, temperature, humidity)
    VALUES (?, ?, ?, ?)
    """, (timestamp, device_id, temperature, humidity))
    conn.commit()

def export_to_csv():
    """Exporterar databasen till en CSV-fil."""
    df = pd.read_sql_query("SELECT * FROM sensor_data", conn)
    df.to_csv("sensor_data.csv", index=False)
    print("Data exporterad till sensor_data.csv!")

# Exempel på hur du använder modulen (kan kommenteras bort vid produktion)
if __name__ == "__main__":
    create_table()
    export_to_csv()
