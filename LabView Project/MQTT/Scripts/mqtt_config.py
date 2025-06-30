# mqtt_config.py

# --- MQTT Broker Configuration ---
MQTT_BROKER = "broker.hivemq.com"  # Replace with your MQTT broker address
MQTT_PORT = 1883           # Default MQTT port
MQTT_KEEPALIVE = 60        # Seconds between keepalive pings

# --- MQTT Topics ---
# Topics for publishing sensor data
TOPIC_TEMP = "sensor/data/temperature/ee2044/g11"
TOPIC_PH = "sensor/data/ph/ee2044/g11"
TOPIC_LIGHT = "sensor/data/light/ee2044/g11"

# Topic for subscribing to control inputs from Node-RED
TOPIC_CONTROL_INPUT = "control/inputs/node-red/ee2044/g11"