"""
Configuration file for MQTT Monitoring App
"""

# MQTT Configuration
MQTT_BROKER = "192.168.5.1"
MQTT_PORT = 1883
MQTT_USERNAME = "AML_Robocon"
MQTT_PASSWORD = "aml305b4"
MQTT_TOPIC = "#"  # Default topic (all)
MQTT_CLIENT_ID = "mqtt_monitor"

# WiFi Configuration (for future use with ESP devices)
WIFI_SSID = ""  # Default empty
WIFI_PASSWORD = ""  # Default empty

# App Configuration
APP_TITLE = "MQTT Monitoring App - AML Robocon"
APP_VERSION = "1.0.0"
APP_WIDTH = 1200
APP_HEIGHT = 800
APP_STYLE = "Fusion"  # "Windows", "Fusion", "WindowsVista"

# Graph Configuration
MAX_DATA_POINTS = 100
REFRESH_RATE_MS = 100  # Refresh rate in milliseconds

# Map Configuration
MAP_WIDTH = 15  # meters
MAP_HEIGHT = 8  # meters
ROBOT_DIAMETER = 0.8  # meters

# UI Colors - Dark theme
DARK_PALETTE = {
    "Window": (53, 53, 53),
    "WindowText": (255, 255, 255),
    "Base": (35, 35, 35),
    "AlternateBase": (53, 53, 53),
    "ToolTipBase": (255, 255, 255),
    "ToolTipText": (255, 255, 255),
    "Text": (255, 255, 255),
    "Button": (53, 53, 53),
    "ButtonText": (255, 255, 255),
    "BrightText": (255, 0, 0),
    "Highlight": (42, 130, 218),
    "HighlightedText": (0, 0, 0)
}

# Status colors
COLOR_CONNECTED = "green"
COLOR_DISCONNECTED = "red"