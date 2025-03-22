from base64 import b64decode

def decode_payload(payload: str):
    """
    Dekodar payload från TTN som är Base64-enkodat och returnerar en dictionary
    med sensorvärden.
    
    Args:
        payload (str): Base64-enkodat payload från TTN.
    
    Returns:
        dict: Dekoderad data som innehåller sensormätningar.
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

# Testa funktionen
if __name__ == "__main__":
    example_payload = "AYYYBQA="  # Byt ut mot ett riktigt Base64-kodat exempel
    decoded_data = decode_payload(example_payload)
    if decoded_data:
        print(f"Decoded data: {decoded_data}")
