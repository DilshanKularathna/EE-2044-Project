# mqtt_subscriber.py
import json
import mqtt_config # Relative import

# Global variables to store received control messages and a flag
# NOTE: In a more complex application, consider using a Queue for thread-safe message passing
_received_control_message = None
_new_message_flag = False

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to control input topic upon successful connection
        client.subscribe(mqtt_config.TOPIC_CONTROL_INPUT)
        print(f"Subscribed to topic: {mqtt_config.TOPIC_CONTROL_INPUT}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the MQTT broker."""
    global _received_control_message, _new_message_flag
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")
    try:
        # Assuming control inputs are JSON strings
        _received_control_message = json.loads(msg.payload.decode())
        _new_message_flag = True
    except json.JSONDecodeError:
        _received_control_message = msg.payload.decode()
        _new_message_flag = True
        print(f"Warning: Received non-JSON message on {msg.topic}")

def get_control_input():
    """Returns the last received control input and resets the flag."""
    global _received_control_message, _new_message_flag
    if _new_message_flag:
        message = _received_control_message
        _received_control_message = None  # Clear the message after reading
        _new_message_flag = False
        return True, json.dumps(message) if isinstance(message, dict) else str(message)
    else:
        return False, "" # No new message