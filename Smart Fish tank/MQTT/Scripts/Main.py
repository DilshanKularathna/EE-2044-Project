# # mqtt_handler.py
# import paho.mqtt.client as mqtt
# import json
# import time # Included for general utility, not used for publish delays in LabVIEW calls
# import sys  # Essential for sys.stdout.flush()

# # --- MQTT Configuration ---
# # You can uncomment one of these brokers. Ensure Node-RED connects to the same one.
# MQTT_BROKER = "broker.hivemq.com"  # HiveMQ public broker
# # MQTT_BROKER = "broker.emqx.io"     # EMQX public broker
# MQTT_PORT = 1883           # Default MQTT port
# MQTT_KEEPALIVE = 60        # Seconds between keepalive pings

# # Topics for publishing sensor data
# # Ensure these topics exactly match what Node-RED is subscribing to.
# # Case-sensitive and character-for-character.
# TOPIC_TEMP = "sensor/data/temperature/ee2044/g11"
# TOPIC_PH = "sensor/data/ph/ee2044/g11"
# TOPIC_LIGHT = "sensor/data/light/ee2044/g11"

# # Topic for subscribing to control inputs from Node-RED
# # Ensure this topic exactly matches what Node-RED is publishing to.
# TOPIC_CONTROL_INPUT = "control/inputs/node-red/ee2044/g11"

# # Global variables to store received control messages
# _received_control_message = None
# _new_message_flag = False

# # --- MQTT Client Instance and Callbacks Setup ---
# # The MQTT client is initialized globally. This code runs automatically
# # when the Python module is first loaded by LabVIEW.

# mqtt_client = mqtt.Client() # Initialize the client

# def on_connect(client, userdata, flags, rc):
#     """Callback for when the client connects to the MQTT broker."""
#     if rc == 0:
#         print("MQTT: Connected to Broker!")
#         sys.stdout.flush() # Flush output to LabVIEW console
#         # Subscribe to control input topic upon successful connection
#         client.subscribe(TOPIC_CONTROL_INPUT)
#         print(f"MQTT: Subscribed to topic: {TOPIC_CONTROL_INPUT}")
#         sys.stdout.flush() # Flush output
#     else:
#         print(f"MQTT: Failed to connect, return code {rc}")
#         sys.stdout.flush() # Flush output

# def on_message(client, userdata, msg):
#     """Callback for when a message is received from the MQTT broker."""
#     global _received_control_message, _new_message_flag
#     received_payload = msg.payload.decode()
#     print(f"MQTT: Received message: '{received_payload}' on topic: '{msg.topic}'")
#     sys.stdout.flush() # Flush output

#     try:
#         # Attempt to parse as JSON. Control inputs from Node-RED are often JSON.
#         _received_control_message = json.loads(received_payload)
#         _new_message_flag = True
#     except json.JSONDecodeError:
#         # If not JSON, store it as a plain string
#         _received_control_message = received_payload
#         _new_message_flag = True
#         print(f"MQTT Warning: Received non-JSON message on {msg.topic}")
#         sys.stdout.flush() # Flush output

# def on_disconnect(client, userdata, rc):
#     """Callback for when the client disconnects from the MQTT broker."""
#     # rc=0 means graceful disconnect. Other codes indicate an error.
#     print(f"MQTT: Disconnected from Broker with result code: {rc}")
#     sys.stdout.flush()

# # Assign callbacks to the client instance
# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = on_message
# mqtt_client.on_disconnect = on_disconnect # Assign the disconnect callback

# # --- Implicit Initialization and Connection on Module Load ---
# # This block of code runs automatically when LabVIEW loads this Python script.
# try:
#     print("MQTT: Attempting to connect to broker on module load...")
#     sys.stdout.flush()

#     mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    
#     # Start a non-blocking loop in a separate thread. This allows the client
#     # to continuously process network traffic (send/receive messages,
#     # handle pings) without blocking the main Python thread or LabVIEW.
#     # It also enables the on_message callback to fire when messages arrive.
#     mqtt_client.loop_start()

#     print("MQTT: Client started background loop and connected (or attempting to connect).")
#     sys.stdout.flush()

# except Exception as e:
#     print(f"MQTT CRITICAL ERROR: Failed to connect or start client loop on module load: {str(e)}")
#     sys.stdout.flush()
#     # In a real-world scenario, you might want more robust error handling here
#     # since LabVIEW won't get a direct return from this top-level code.


# # --- Functions callable from LabVIEW ---

# def publish_sensor_data(temp, ph, light):
#     """
#     Publishes temperature, pH, and light data to their respective topics.
#     This function is intended to be called repeatedly by LabVIEW.
#     It returns a string indicating the outcome of the publish operation.
#     No internal delays are added; LabVIEW should manage the publishing rate.
#     """
#     try:
#         if not mqtt_client.is_connected():
#             # This check gives a warning if the connection dropped.
#             # The loop_start() should try to auto-reconnect, but it's good to know.
#             print("MQTT Warning: Client not connected when publish_sensor_data was called. Attempting to publish anyway...")
#             sys.stdout.flush()
        
#         # Publish Temperature
#         temp_payload = json.dumps({"value": temp, "unit": "C"})
#         mqtt_client.publish(TOPIC_TEMP, temp_payload)
#         print(f"MQTT Publish: Temp={temp} to {TOPIC_TEMP}")
#         sys.stdout.flush()

#         # Publish pH
#         ph_payload = json.dumps({"value": ph})
#         mqtt_client.publish(TOPIC_PH, ph_payload)
#         print(f"MQTT Publish: pH={ph} to {TOPIC_PH}")
#         sys.stdout.flush()

#         # Publish Light
#         light_payload = json.dumps({"value": light, "unit": "lux"})
#         mqtt_client.publish(TOPIC_LIGHT, light_payload)
#         print(f"MQTT Publish: Light={light} to {TOPIC_LIGHT}")
#         sys.stdout.flush()

#         return "Sensor data published successfully."
#     except Exception as e:
#         error_msg = f"MQTT ERROR: Failed to publish sensor data: {str(e)}"
#         print(error_msg)
#         sys.stdout.flush()
#         return error_msg

# def get_control_input():
#     """
#     Checks for and returns the latest control input message received from the broker.
#     This function is intended to be called repeatedly by LabVIEW to poll for new messages.
#     It returns the message content as a JSON string (if it was a dictionary) or a plain string.
#     Returns an empty string ("") if no new message has been received since the last call.
#     """
#     global _received_control_message, _new_message_flag
    
#     if _new_message_flag:
#         message_to_return = _received_control_message
#         _received_control_message = None  # Clear the stored message
#         _new_message_flag = False         # Reset the flag

#         # Return the message as a JSON string if it was a dictionary, otherwise as a plain string.
#         # This ensures LabVIEW always receives a string.
#         return json.dumps(message_to_return) if isinstance(message_to_return, dict) else str(message_to_return)
#     else:
#         return "" # No new message, return an empty string


# # # --- Standalone Testing Block (Optional) ---
# # # This block runs only when the script is executed directly (e.g., `python mqtt_handler.py`).
# # # It will NOT run when LabVIEW calls the functions. It's for development testing.
# # if __name__ == '__main__':
# #     print("\n--- Running Standalone MQTT Handler Test ---")
# #     print("This simulates LabVIEW loading the script and then calling functions.")
# #     print("Check your console for MQTT related output.")
# #     print(f"Ensure Node-RED is configured for: {MQTT_BROKER}:{MQTT_PORT}")
# #     print(f"Publishing to: {TOPIC_TEMP}, {TOPIC_PH}, {TOPIC_LIGHT}")
# #     print(f"Subscribing to: {TOPIC_CONTROL_INPUT}")

# #     # Give the implicit connection a moment to establish
# #     time.sleep(3) # Increased sleep to ensure connection is more likely established

# #     if mqtt_client.is_connected():
# #         print("\nStandalone Test: MQTT client appears connected.")
# #         print("Send a message to topic: `control/inputs/node-red/ee2044/g11` from Node-RED or an MQTT client.")
# #         print("Press Ctrl+C to stop this standalone test.")
        
# #         try:
# #             publish_counter = 0
# #             while True:
# #                 # Simulate LabVIEW calling publish_sensor_data periodically
# #                 # This delay is *internal to the test loop*, not the publish_sensor_data function itself.
# #                 if publish_counter % 2 == 0: # Publish sensor data every 2 seconds
# #                     temp_val = 25.0 + publish_counter * 0.1
# #                     ph_val = 7.0 + publish_counter * 0.05
# #                     light_val = 500 + publish_counter * 10
# #                     publish_status = publish_sensor_data(temp_val, ph_val, light_val)
# #                     print(f"Standalone Test: Publish status: {publish_status}")
                
# #                 # Simulate LabVIEW calling get_control_input frequently to poll for messages
# #                 control_msg = get_control_input()
# #                 if control_msg:
# #                     print(f"Standalone Test: RECEIVED CONTROL MESSAGE: {control_msg}")
                
# #                 time.sleep(1) # Polling interval for this standalone test loop
# #                 publish_counter += 1

# #         except KeyboardInterrupt:
# #             print("\nStandalone Test: Interrupted by user (Ctrl+C).")
# #         finally:
# #             # Explicit cleanup for standalone run. This logic is NOT run when used by LabVIEW.
# #             print("Standalone Test: Stopping MQTT client background loop and disconnecting...")
# #             sys.stdout.flush()
# #             mqtt_client.loop_stop()
# #             mqtt_client.disconnect()
# #             print("Standalone Test: MQTT client cleaned up.")
# #             sys.stdout.flush()
# #     else:
# #         print("Standalone Test: Initial MQTT connection failed. Cannot proceed with tests.")
# #         sys.stdout.flush()

import paho.mqtt.client as mqtt
import json
import time
import sys

# --- MQTT Configuration ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

TOPIC_TEMP = "sensor/data/temperature/ee2044/g11"
TOPIC_PH = "sensor/data/ph/ee2044/g11"
TOPIC_LIGHT = "sensor/data/light/ee2044/g11"
TOPIC_CONTROL_INPUT = "control/inputs/node-red/ee2044/g11"

_received_control_message = None
_new_message_flag = False

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT: Connected to Broker!")
        sys.stdout.flush()
        client.subscribe(TOPIC_CONTROL_INPUT)
        print(f"MQTT: Subscribed to topic: {TOPIC_CONTROL_INPUT}")
        sys.stdout.flush()
    else:
        print(f"MQTT: Failed to connect, return code {rc}")
        sys.stdout.flush()

def on_message(client, userdata, msg):
    global _received_control_message, _new_message_flag
    received_payload = msg.payload.decode()
    print(f"MQTT: Received message: '{received_payload}' on topic: '{msg.topic}'")
    sys.stdout.flush()

    try:
        _received_control_message = json.loads(received_payload)
    except json.JSONDecodeError:
        _received_control_message = received_payload
        print(f"MQTT Warning: Received non-JSON message on {msg.topic}")
    _new_message_flag = True
    sys.stdout.flush()

def on_disconnect(client, userdata, rc):
    print(f"MQTT: Disconnected from Broker with result code: {rc}")
    sys.stdout.flush()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

try:
    print("MQTT: Attempting to connect to broker on module load...")
    sys.stdout.flush()

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    mqtt_client.loop_start()

    print("MQTT: Client started background loop and connected (or attempting to connect).")
    sys.stdout.flush()

except Exception as e:
    print(f"MQTT CRITICAL ERROR: {str(e)}")
    sys.stdout.flush()

# --- LabVIEW Callable Functions ---

def publish_sensor_data(temp, ph, light):
    try:
        if not mqtt_client.is_connected():
            print("MQTT Warning: Client not connected.")
            sys.stdout.flush()

        # Temperature
        temp_payload = json.dumps({"value": temp, "unit": "C"})
        mqtt_client.publish(TOPIC_TEMP, temp_payload).wait_for_publish()
        print(f"MQTT Publish: Temp={temp} to {TOPIC_TEMP}")
        sys.stdout.flush()

        # pH
        ph_payload = json.dumps({"value": ph})
        mqtt_client.publish(TOPIC_PH, ph_payload).wait_for_publish()
        print(f"MQTT Publish: pH={ph} to {TOPIC_PH}")
        sys.stdout.flush()

        # Light
        light_payload = json.dumps({"value": light, "unit": "lux"})
        mqtt_client.publish(TOPIC_LIGHT, light_payload).wait_for_publish()
        print(f"MQTT Publish: Light={light} to {TOPIC_LIGHT}")
        sys.stdout.flush()

        # Allow MQTT loop to process network I/O
        mqtt_client.loop(timeout=1.0)

        return "Sensor data published successfully."

    except Exception as e:
        error_msg = f"MQTT ERROR: Failed to publish: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        return error_msg

def get_control_input():
    global _received_control_message, _new_message_flag

    if _new_message_flag:
        msg = _received_control_message
        _received_control_message = None
        _new_message_flag = False
        return json.dumps(msg) if isinstance(msg, dict) else str(msg)
    return ""
