# mqtt_client_manager.py
import paho.mqtt.client as mqtt
import mqtt_config      # Changed from .mqtt_config
import mqtt_publisher   # Changed from .mqtt_publisher
import mqtt_subscriber  # Changed from .mqtt_subscriber

# ... rest of your code

# Global MQTT client instance
_mqtt_client = None

def initialize_mqtt_client(broker=None, port=None):
    """Initializes and connects the MQTT client."""
    global _mqtt_client
    if _mqtt_client is None:
        return True

    # Use provided broker/port or defaults from config
    actual_broker = broker
    actual_port = port

    _mqtt_client = mqtt.Client()
    _mqtt_client.on_connect = mqtt_subscriber.on_connect
    _mqtt_client.on_message = mqtt_subscriber.on_message

    try:
        _mqtt_client.connect(actual_broker, actual_port, mqtt_config.MQTT_KEEPALIVE)
        # Start a non-blocking loop to handle network traffic and callbacks
        _mqtt_client.loop_start()
        return True
    except Exception as e:
        _mqtt_client = None # Reset client on failure
        return False
    
def publish_sensor_data_lv_wrapper(temp, ph, light):
    """Wrapper for LabVIEW to publish sensor data."""
    if _mqtt_client is None:
        return False
    else :
        mqtt_publisher.publish_sensor_data(_mqtt_client, temp, ph, light)
        return True

def get_control_input_lv_wrapper():
    """Wrapper for LabVIEW to get control input."""
    mqtt_subscriber.get_control_input()
    return True

def cleanup_mqtt_client():
    """Disconnects and stops the MQTT client."""
    global _mqtt_client
    if _mqtt_client is None:
        return True
    try:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
        _mqtt_client = None # Clear the client instance
        return True, "MQTT client disconnected and cleaned up."
    except Exception as e:
        return False

