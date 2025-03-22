import paho.mqtt.client as mqtt
import json
from datetime import datetime
from base64 import b64decode
from influxdb_client import InfluxDBClient, Point, WriteOptions
import sqlite3

# InfluxDB-konfiguration
INFLUXDB_TOKEN = "Kicz1uUxo0KMUe3SbF8eINXvheLJzVO7ZcN2hXpRaZYjAqBJ9F_TJs8ORdS1f_MAF4DXlk717ZNC1Bsl1AN2Ng=="
INFLUXDB_ORG = "Högskolan"  
INFLUXDB_BUCKET = "iot_data"
INFLUXDB_URL = "http://localhost:8086"  


# MQTT-konfiguration
BROKER = "eu1.cloud.thethings.network"
PORT = 1883
USERNAME = "h21ronjo-app@ttn"
PASSWORD = "NNSXS.O6MXULGVR7VWFFODC2TZGCKQEPA7ZLAWWB7Z3BY.BTJ54ERT6RLBK6MTAYKOKL66BCZGVCNHAHOT6M254LKTQ6F2FDBQ"
TOPIC = "v3/+/devices/+/up"

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


def insert_data(timestamp, device_id, temperature, humidity):
    """Lägger till data i SQLite-databasen."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sensor_data (timestamp, device_id, temperature, humidity)
    VALUES (?, ?, ?, ?)
    """, (timestamp, device_id, temperature, humidity))
    conn.commit()
    conn.close()


def decode_payload(payload: str):
    """
    Dekodar payload från TTN som är Base64-enkodat och returnerar en dictionary
    med sensorvärden.
    """
    try:
        # Avkodar Base64-strängen till bytes
        decoded_bytes = b64decode(payload)

        # Exempel på hur vi tolkar data (CayenneLPP)
        temperature = decoded_bytes[2] + decoded_bytes[3] / 10.0
        humidity = decoded_bytes[5] / 2.0

        return {
            "temperature": temperature,
            "humidity": humidity
        }
    except Exception as e:
        print(f"Error decoding payload: {e}")
        return None


def write_to_influxdb(device_id, temperature, humidity):
    """Skriver sensordata till InfluxDB."""
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

    point = (
        Point("sensor_data")
        .tag("device_id", device_id)
        .field("temperature", temperature)
        .field("humidity", humidity)
    )
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    print(f"Data skriven till InfluxDB: {device_id}, {temperature} °C, {humidity} %")


def on_connect(client, userdata, flags, rc):
    """Callback-funktion för MQTT-anslutning."""
    if rc == 0:
        print("Connected to TTN MQTT broker!")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")


def on_message(client, userdata, msg):
    """Callback-funktion för MQTT-meddelanden."""
    try:
        # Tolka inkommande meddelande
        payload = json.loads(msg.payload.decode("utf-8"))
        device_id = payload["end_device_ids"]["device_id"]
        raw_payload = payload["uplink_message"]["frm_payload"]

        # Dekodera payload
        decoded_data = decode_payload(raw_payload)
        if not decoded_data:
            print("Failed to decode payload.")
            return

        # Lägg till timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Spara data i SQLite
        insert_data(timestamp, device_id, decoded_data["temperature"], decoded_data["humidity"])

        # Spara data i InfluxDB
        write_to_influxdb(device_id, decoded_data["temperature"], decoded_data["humidity"])

        print(f"Data saved: {timestamp}, {device_id}, {decoded_data['temperature']} °C, {decoded_data['humidity']} %")
    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    """Huvudfunktionen för att köra applikationen."""
    create_table()  # Säkerställ att SQLite-tabellen finns
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("Connecting to MQTT broker...")
        client.connect(BROKER, PORT, 60)
        print("Connected. Waiting for messages...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("Disconnecting...")
        client.disconnect()


if __name__ == "__main__":
    main()
