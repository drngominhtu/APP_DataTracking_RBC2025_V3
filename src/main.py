from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import paho.mqtt.client as mqtt
from visualization import Visualization
from mqtt_client import MqttClient
from config import (MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USERNAME,
                   APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_STYLE, DARK_PALETTE,
                   COLOR_CONNECTED, COLOR_DISCONNECTED)

class TopicBrowserDialog(QtWidgets.QDialog):
    """Dialog to browse and select MQTT topics"""
    def __init__(self, parent=None, topics=None):
        super().__init__(parent)
        self.setWindowTitle("MQTT Topic Browser")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        
        # Search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search topics...")
        self.search_box.textChanged.connect(self.filter_topics)
        self.layout.addWidget(self.search_box)
        
        # Topic list
        self.topic_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.topic_list)
        
        # Add topics if provided
        if topics:
            self.topic_list.addItems(topics)
            
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.subscribe_button = QtWidgets.QPushButton("Subscribe")
        self.subscribe_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.subscribe_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
    
    def filter_topics(self, text):
        """Filter the topic list by search text"""
        for i in range(self.topic_list.count()):
            item = self.topic_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def get_selected_topic(self):
        """Return the selected topic or None"""
        selected_items = self.topic_list.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

class MainApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
        self.setWindowIcon(QtGui.QIcon.fromTheme("applications-system"))  # Fallback if icon missing

        # Main layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(2)  # Giảm khoảng cách giữa các thành phần
        self.layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin
        self.setLayout(self.layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Connection status bar - thu nhỏ
        self.connection_bar = QtWidgets.QHBoxLayout()
        self.connection_bar.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QtWidgets.QLabel(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}")
        self.status_label.setFont(QtGui.QFont('', 8))
        
        self.status_indicator = QtWidgets.QLabel("Disconnected")
        self.status_indicator.setFont(QtGui.QFont('', 8))
        self.status_indicator.setStyleSheet(f"color: {COLOR_DISCONNECTED}; font-weight: bold;")
        
        self.connection_bar.addWidget(self.status_label)
        self.connection_bar.addStretch()
        self.connection_bar.addWidget(self.status_indicator)
        
        self.layout.addLayout(self.connection_bar)

        # Visualization widget
        self.visualization = Visualization()
        self.layout.addWidget(self.visualization)

        # Topic subscription controls - thu nhỏ
        topic_layout = QtWidgets.QHBoxLayout()
        topic_layout.setContentsMargins(0, 0, 0, 0)
        
        # Giảm kích thước label
        topic_label = QtWidgets.QLabel("Topic:")
        topic_label.setFont(QtGui.QFont('', 8))
        topic_label.setFixedWidth(30)
        topic_layout.addWidget(topic_label)
        
        self.topic_input = QtWidgets.QLineEdit(self)
        self.topic_input.setPlaceholderText("Enter MQTT Topic")
        self.topic_input.setFixedHeight(20)
        topic_layout.addWidget(self.topic_input)
        
        self.subscribe_button = QtWidgets.QPushButton("Subscribe", self)
        self.subscribe_button.setFixedHeight(20)
        self.subscribe_button.clicked.connect(self.subscribe_to_topic)
        topic_layout.addWidget(self.subscribe_button)

        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.browse_button.setFixedHeight(20)
        self.browse_button.clicked.connect(self.browse_topics)
        topic_layout.addWidget(self.browse_button)
        
        self.layout.addLayout(topic_layout)
        
        # Current subscriptions display
        self.subscription_label = QtWidgets.QLabel("Current subscriptions: None")
        self.subscription_label.setFont(QtGui.QFont('', 8))
        self.layout.addWidget(self.subscription_label)

        # Setup MQTT client
        # Load saved connection settings
        saved_settings = self.load_connection_settings()
    
        # Setup MQTT client with saved settings if available
        if saved_settings:
            self.mqtt_client = MqttClient(
                saved_settings.get("broker", MQTT_BROKER),
                saved_settings.get("port", MQTT_PORT)
            )
            
            # Set credentials if provided
            if saved_settings.get("username"):
                self.mqtt_client.client.username_pw_set(
                    saved_settings["username"],
                    saved_settings["password"]
                )
            
            # Configure SSL if enabled
            if saved_settings.get("use_ssl", False):
                self.mqtt_client.client.tls_set(
                    ca_certs=saved_settings.get("ca_file") or None,
                    certfile=saved_settings.get("cert_file") or None,
                    keyfile=saved_settings.get("key_file") or None
                )
            
            # Update status bar
            self.status_label.setText(f"MQTT: {saved_settings['broker']}:{saved_settings['port']}")
        else:
            # Use default settings
            self.mqtt_client = MqttClient(MQTT_BROKER, MQTT_PORT)
    
        # Connect signals
        self.mqtt_client.message_received.connect(self.on_message_received)
        self.mqtt_client.connection_changed.connect(self.on_connection_changed)
        self.mqtt_client.topic_detected.connect(self.on_topic_detected)
        
        # Detected topics
        self.detected_topics = set()
        
        # Connect to broker
        self.mqtt_client.connect()
        
        # Auto-subscribe to default topic
        QtCore.QTimer.singleShot(1000, lambda: self.auto_subscribe())
    
    def create_menu_bar(self):
        """Create menu bar at the top"""
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setNativeMenuBar(False)  # Force non-native menu bar
    
        # File menu
        file_menu = self.menu_bar.addMenu("File")
        file_menu.addAction("Export All Data", self.export_all_data)
        file_menu.addAction("Save Settings", self.save_settings)
        file_menu.addAction("Load Settings", self.load_settings)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
    
        # Connection menu
        connection_menu = self.menu_bar.addMenu("Connection")
        connection_menu.addAction("Connect", lambda: self.mqtt_client.connect())
        connection_menu.addAction("Disconnect", lambda: self.mqtt_client.disconnect())
        connection_menu.addSeparator()
        connection_menu.addAction("Settings", self.show_connection_settings)
    
        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about_dialog)
        help_menu.addAction("Help", self.show_help_dialog)
    
        self.layout.setMenuBar(self.menu_bar)
    
        # No need for these methods anymore
        # def show_file_menu(self):
        # def show_connection_menu(self):
        # def show_help_menu(self):
    
    def export_all_data(self):
        """Export all data to file"""
        QtWidgets.QMessageBox.information(self, "Export", "This feature is not yet implemented.")
    
    def save_settings(self):
        """Save application settings"""
        QtWidgets.QMessageBox.information(self, "Save Settings", "This feature is not yet implemented.")
    
    def load_settings(self):
        """Load application settings"""
        QtWidgets.QMessageBox.information(self, "Load Settings", "This feature is not yet implemented.")
    
    def show_connection_settings(self):
        """Show connection settings dialog"""
        from connection_dialog import ConnectionSettingsDialog
        
        # Get current settings
        current_settings = {
            "name": "Default Connection",
            "protocol": "mqtt://",
            "broker": MQTT_BROKER,
            "port": MQTT_PORT,
            "username": MQTT_USERNAME,
            "password": MQTT_PASSWORD,
            "default_topic": MQTT_TOPIC,
            # Add any other settings you want to include
        }
        
        dialog = ConnectionSettingsDialog(self, current_settings)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_settings = dialog.get_settings()
            
            # Apply new settings 
            self.mqtt_client.disconnect()  # Disconnect first
            
            # Update MQTT client
            self.mqtt_client = MqttClient(
                new_settings["broker"], 
                new_settings["port"]
            )
            
            # Set credentials if provided
            if new_settings["username"]:
                self.mqtt_client.client.username_pw_set(
                    new_settings["username"],
                    new_settings["password"]
                )
            
            # Configure SSL if enabled
            if new_settings["use_ssl"]:
                self.mqtt_client.client.tls_set(
                    ca_certs=new_settings["ca_file"] or None,
                    certfile=new_settings["cert_file"] or None,
                    keyfile=new_settings["key_file"] or None
                )
            
            # Reconnect signals
            self.mqtt_client.message_received.connect(self.on_message_received)
            self.mqtt_client.connection_changed.connect(self.on_connection_changed)
            self.mqtt_client.topic_detected.connect(self.on_topic_detected)
            
            # Update status bar
            self.status_label.setText(f"MQTT: {new_settings['broker']}:{new_settings['port']}")
            
            # Connect to broker
            self.mqtt_client.connect()
            
            # Save settings to config file
            self.save_connection_settings(new_settings)
    
    def show_about_dialog(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(self, "About", f"{APP_TITLE} v{APP_VERSION}\n\nDeveloped by AML Robocon Team")
    
    def show_help_dialog(self):
        """Show help dialog"""
        QtWidgets.QMessageBox.information(self, "Help", "This application allows you to monitor MQTT topics and visualize the data.")

    def auto_subscribe(self):
        """Auto subscribe to default topic after connection"""
        self.mqtt_client.subscribe(MQTT_TOPIC)
        self.update_subscription_label(MQTT_TOPIC)

    def subscribe_to_topic(self):
        topic = self.topic_input.text()
        if topic:
            if self.mqtt_client.subscribe(topic):
                self.update_subscription_label(topic)
                self.topic_input.clear()
    
    def browse_topics(self):
        """Open dialog to browse and select topics"""
        topics = list(self.detected_topics)
        if not topics:
            QtWidgets.QMessageBox.information(self, "No Topics", "No topics have been detected yet.")
            return
            
        dialog = TopicBrowserDialog(self, topics)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_topic = dialog.get_selected_topic()
            if selected_topic:
                if self.mqtt_client.subscribe(selected_topic):
                    self.update_subscription_label(selected_topic)

    def update_subscription_label(self, new_topic):
        """Update the label showing current subscriptions"""
        current_text = self.subscription_label.text()
        if "None" in current_text:
            self.subscription_label.setText(f"Current subscriptions: {new_topic}")
        else:
            # Extract current topics
            topics = current_text.replace("Current subscriptions: ", "")
            topics_list = topics.split(", ")
            if new_topic not in topics_list:
                topics_list.append(new_topic)
                self.subscription_label.setText(f"Current subscriptions: {', '.join(topics_list)}")

    def on_message_received(self, topic, payload):
        """Handle message received signal"""
        try:
            # Update the visualization
            self.visualization.update(payload)
        except Exception as e:
            print(f"Error processing message: {e}")
            
    def on_topic_detected(self, topic):
        """Handle new topic detected"""
        self.detected_topics.add(topic)

    def on_connection_changed(self, connected):
        """Update connection status indicator"""
        if connected:
            self.status_indicator.setText("Connected")
            self.status_indicator.setStyleSheet(f"color: {COLOR_CONNECTED}; font-weight: bold;")
        else:
            self.status_indicator.setText("Disconnected")
            self.status_indicator.setStyleSheet(f"color: {COLOR_DISCONNECTED}; font-weight: bold;")

    def closeEvent(self, event):
        """Clean up when closing the application"""
        self.mqtt_client.disconnect()
        event.accept()

    def save_connection_settings(self, settings):
        """Save connection settings to file"""
        try:
            import json
            import os
            
            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.expanduser("~"), ".mqtt_monitor")
            os.makedirs(config_dir, exist_ok=True)
            
            # Save settings to file
            with open(os.path.join(config_dir, "connections.json"), "w") as f:
                json.dump(settings, f, indent=2)
            
            print(f"Settings saved to {os.path.join(config_dir, 'connections.json')}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_connection_settings(self):
        """Load connection settings from file"""
        try:
            import json
            import os
            
            config_file = os.path.join(os.path.expanduser("~"), ".mqtt_monitor", "connections.json")
            if not os.path.exists(config_file):
                return None
            
            with open(config_file, "r") as f:
                settings = json.load(f)
            
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply style
    app.setStyle(APP_STYLE)
    
    # Set application-wide dark palette
    palette = QtGui.QPalette()
    for key, (r, g, b) in DARK_PALETTE.items():
        color_role = getattr(QtGui.QPalette, key)
        if key == "BrightText":
            palette.setColor(color_role, QtGui.QColor(r, g, b))
        else:
            palette.setColor(QtGui.QPalette.Active, color_role, QtGui.QColor(r, g, b))
            palette.setColor(QtGui.QPalette.Inactive, color_role, QtGui.QColor(r, g, b))
            
    app.setPalette(palette)
    
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())