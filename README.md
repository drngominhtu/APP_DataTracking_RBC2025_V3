# MQTT Monitoring Application

This project is a Python application that provides a graphical interface for monitoring MQTT topics. It allows users to subscribe to specific topics, visualize the data in real-time, and manage the incoming messages effectively.

## Project Structure

```
mqtt_monitoring_app
├── src
│   ├── main.py            # Entry point of the application
│   ├── mqtt_client.py     # Handles MQTT connection and message processing
│   ├── visualization.py    # Manages the chart and monitoring table
│   ├── config.py          # Contains configuration settings
│   └── utils
│       └── data_handler.py # Utility functions for data processing
├── resources
│   └── icons
│       ├── app_icon.png   # Application icon
│       └── refresh_icon.png # Icon for the refresh button
├── requirements.txt        # Lists required Python libraries
└── README.md               # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mqtt_monitoring_app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/main.py
   ```

2. Select the MQTT topic you wish to subscribe to from the GUI.

3. Monitor the incoming messages and visualize the data in the chart and table.

## Dependencies

This application requires the following Python libraries:
- paho-mqtt
- tkinter
- matplotlib
- pandas

Make sure to install these libraries using the `requirements.txt` file.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.