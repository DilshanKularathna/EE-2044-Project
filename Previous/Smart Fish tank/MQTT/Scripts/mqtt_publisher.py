# mqtt_publisher.py
import json
import mqtt_config # Relative import: assuming in the same directory structure

def publish_sensor_data(mqtt_client, temp, ph, light):
    """Publishes temperature, pH, and light data to respective topics."""
    try:
        # Publish temperature
        temp_payload = json.dumps({"value": temp, "unit": "C"})
        mqtt_client.publish(mqtt_config.TOPIC_TEMP, temp_payload)
        print(f"Published Temp: {temp} to {mqtt_config.TOPIC_TEMP}")

        # Publish pH
        ph_payload = json.dumps({"value": ph})
        mqtt_client.publish(mqtt_config.TOPIC_PH, ph_payload)
        print(f"Published pH: {ph} to {mqtt_config.TOPIC_PH}")

        # Publish light
        light_payload = json.dumps({"value": light, "unit": "lux"})
        mqtt_client.publish(mqtt_config.TOPIC_LIGHT, light_payload)
        print(f"Published Light: {light} to {mqtt_config.TOPIC_LIGHT}")

        return True, "Sensor data published successfully."
    except Exception as e:
        return False, f"Failed to publish sensor data: {str(e)}"