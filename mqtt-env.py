import time
import os
import paho.mqtt.client as mqtt
from routeros_api import RouterOsApiPool, exceptions
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# MikroTik Router credentials from environment variables
ROUTER_HOST = os.getenv('ROUTER_HOST')
ROUTER_PORT = int(os.getenv('ROUTER_PORT', 5262))
ROUTER_USERNAME = os.getenv('ROUTER_USERNAME')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')
INTERFACE_NAME = os.getenv('INTERFACE_NAME', 'VLAN10-WAN')
SAMPLE_INTERVAL = int(os.getenv('SAMPLE_INTERVAL', 1))

# MQTT Broker credentials from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TX_TOPIC = os.getenv('MQTT_TX_TOPIC', 'router/tx')
MQTT_RX_TOPIC = os.getenv('MQTT_RX_TOPIC', 'router/rx')

try:
    # Connect to the MikroTik API
    api_pool = RouterOsApiPool(
        ROUTER_HOST, username=ROUTER_USERNAME, password=ROUTER_PASSWORD, port=ROUTER_PORT, plaintext_login=True
    )
    api = api_pool.get_api()

    # Connect to the MQTT broker
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # Start the MQTT loop to handle background tasks

#    print(f"Monitoring current TX/RX speed for interface: {INTERFACE_NAME}")
#    print("Publishing data to MQTT. Press Ctrl+C to stop.")

    while True:
        # Fetch the first set of tx-byte and rx-byte values
        initial_data = api.get_resource('/interface').get(name=INTERFACE_NAME)
        if not initial_data:
            print(f"Interface '{INTERFACE_NAME}' not found.")
            break

        initial_tx = int(initial_data[0].get('tx-byte', 0))
        initial_rx = int(initial_data[0].get('rx-byte', 0))

        # Wait for the sampling interval
        time.sleep(SAMPLE_INTERVAL)

        # Fetch the second set of tx-byte and rx-byte values
        final_data = api.get_resource('/interface').get(name=INTERFACE_NAME)
        if not final_data:
            print(f"Interface '{INTERFACE_NAME}' not found.")
            break

        final_tx = int(final_data[0].get('tx-byte', 0))
        final_rx = int(final_data[0].get('rx-byte', 0))

        # Calculate current TX/RX speed in bytes per second
        tx_speed_bps = (final_tx - initial_tx) / SAMPLE_INTERVAL
        rx_speed_bps = (final_rx - initial_rx) / SAMPLE_INTERVAL

        # Convert to Mbps
        tx_speed_mbps = (tx_speed_bps * 8) / 1_000_000
        rx_speed_mbps = (rx_speed_bps * 8) / 1_000_000

        # Publish to MQTT topics
        client.publish(MQTT_TX_TOPIC, f"{tx_speed_mbps:.2f}")
        client.publish(MQTT_RX_TOPIC, f"{rx_speed_mbps:.2f}")

        print(f"Published TX: {tx_speed_mbps:.2f} Mbps, RX: {rx_speed_mbps:.2f} Mbps to MQTT.")

except exceptions.RouterOsApiConnectionError as e:
    print(f"Connection error: {e}")
except KeyboardInterrupt:
    print("\nMonitoring stopped.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if 'api_pool' in locals():
        api_pool.disconnect()
    if 'client' in locals():
        client.loop_stop()
        client.disconnect()

