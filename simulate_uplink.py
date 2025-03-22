import json
from main import on_message  # Importera on_message-funktionen från main.py
from datetime import datetime
import random

# Funktion för att generera en payload
def generate_uplink(device_id, temperature, humidity):
    """Skapar en uplink payload i TTN-format."""
    base64_payload = create_base64_payload(temperature, humidity)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    uplink = {
        "end_device_ids": {
            "device_id": device_id,
            "application_ids": {"application_id": "test-app"},
            "dev_eui": "A81758FFFE0459FD"
        },
        "uplink_message": {
            "frm_payload": base64_payload,
            "f_port": 1,
            "rx_metadata": [
                {
                    "gateway_ids": {"gateway_id": "test-gateway"},
                    "rssi": -57,
                    "snr": 9.2
                }
            ],
            "settings": {
                "data_rate": {"lora": {"bandwidth": 125, "spreading_factor": 7}}
            },
            "received_at": timestamp
        }
    }
    return uplink

def create_base64_payload(temperature, humidity):
    """Skapar en Base64-enkodad payload baserad på temperatur och luftfuktighet."""
    temp_high_byte = int(temperature)  # Heltalsdelen av temperaturen
    temp_low_byte = int((temperature - temp_high_byte) * 10)  # Decimaldelen som byte
    humidity_byte = int(humidity * 2)  # Luftfuktighet omvandlad till byte

    # Bygg payload som bytes
    payload_bytes = bytes([0x01, 0x80, temp_high_byte, temp_low_byte, 0x68, humidity_byte])
    # Base64-enkoda
    return payload_bytes.hex()

# Simulera flera uplinks
def simulate_multiple_uplinks():
    devices = ["device-01", "device-02", "device-03"]
    for device_id in devices:
        # Generera slumpmässiga värden för temperatur och luftfuktighet
        temperature = random.uniform(12.0, 30.0)  # Temperatur mellan 15 och 30 °C
        humidity = random.uniform(22.0, 60.0)  # Luftfuktighet mellan 20 och 60 %

        # Skapa uplink
        uplink_payload = generate_uplink(device_id, temperature, humidity)
        uplink_json = json.dumps(uplink_payload)
        print(f"Simulerar uplink för {device_id}: {uplink_json}")

        # Skicka payload till on_message
        class MockMQTTMessage:
            def __init__(self, payload):
                self.payload = payload

        msg = MockMQTTMessage(payload=uplink_json.encode('utf-8'))
        on_message(None, None, msg)

if __name__ == "__main__":
    simulate_multiple_uplinks()
