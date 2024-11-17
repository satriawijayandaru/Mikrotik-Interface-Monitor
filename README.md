# MikroTik Speed Monitor with MQTT

This project monitors the network interface speed (TX/RX data) of a MikroTik router and publishes the current network speed to MQTT topics in real-time.

## Features
- Connects to a MikroTik router via its API.
- Retrieves the current TX and RX data of a specified network interface.
- Calculates the current data speed in Mbps.
- Publishes the speed data to MQTT topics for remote monitoring.
- Configurable MikroTik credentials, interface name, and MQTT broker details via environment variables.

## Requirements

- Python 3.x
- Docker (optional for containerized setup)
- MQTT broker (e.g., Mosquitto, EMQX, etc.)
