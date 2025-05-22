"""
Connection Dialog for MQTT Monitoring App
Allows users to configure WiFi and MQTT connection settings
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QTabWidget, QWidget, 
                            QCheckBox, QSpinBox, QLabel, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import config

class ConnectionDialog(QDialog):
    """Dialog for configuring connection settings"""
    
    connectionUpdated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Settings")
        self.setMinimumWidth(400)
        
        # Initialize UI
        self.initUI()
        self.loadCurrentSettings()
        
    def initUI(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        mqtt_tab = self.createMQTTTab()
        wifi_tab = self.createWiFiTab()
        
        tabs.addTab(mqtt_tab, "MQTT Settings")
        tabs.addTab(wifi_tab, "WiFi Settings")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save and Connect")
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
        
        self.save_button.clicked.connect(self.saveSettings)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def createMQTTTab(self):
        """Create the MQTT settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # MQTT Broker
        self.broker_input = QLineEdit()
        layout.addRow("MQTT Broker:", self.broker_input)
        
        # MQTT Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1883)
        layout.addRow("MQTT Port:", self.port_input)
        
        # Client ID
        self.client_id_input = QLineEdit()
        layout.addRow("Client ID:", self.client_id_input)
        
        # Authentication
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        auth_layout.addRow("Username:", self.username_input)
        auth_layout.addRow("Password:", self.password_input)
        
        auth_group.setLayout(auth_layout)
        layout.addRow(auth_group)
        
        # Topic
        self.topic_input = QLineEdit()
        layout.addRow("Default Topic:", self.topic_input)
        
        tab.setLayout(layout)
        return tab
        
    def createWiFiTab(self):
        """Create the WiFi settings tab (for future ESP devices)"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Info label
        info_label = QLabel("WiFi settings for ESP devices or other IoT hardware.")
        info_label.setWordWrap(True)
        layout.addRow(info_label)
        
        # SSID
        self.ssid_input = QLineEdit()
        layout.addRow("WiFi SSID:", self.ssid_input)
        
        # Password
        self.wifi_password_input = QLineEdit()
        self.wifi_password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("WiFi Password:", self.wifi_password_input)
        
        tab.setLayout(layout)
        return tab
    
    def loadCurrentSettings(self):
        """Load current settings from config into the dialog"""
        # MQTT Settings
        self.broker_input.setText(config.MQTT_BROKER)
        self.port_input.setValue(config.MQTT_PORT)
        self.client_id_input.setText(config.MQTT_CLIENT_ID)
        self.username_input.setText(config.MQTT_USERNAME)
        self.password_input.setText(config.MQTT_PASSWORD)
        self.topic_input.setText(config.MQTT_TOPIC)
        
        # WiFi Settings
        self.ssid_input.setText(config.WIFI_SSID)
        self.wifi_password_input.setText(config.WIFI_PASSWORD)
    
    def saveSettings(self):
        """Save the settings and emit signal"""
        try:
            # Validate broker and port
            broker = self.broker_input.text()
            if not broker:
                QMessageBox.warning(self, "Validation Error", "MQTT Broker address cannot be empty")
                return
            
            # Get all settings
            settings = {
                "MQTT_BROKER": broker,
                "MQTT_PORT": self.port_input.value(),
                "MQTT_CLIENT_ID": self.client_id_input.text() or "mqtt_monitor",
                "MQTT_USERNAME": self.username_input.text(),
                "MQTT_PASSWORD": self.password_input.text(),
                "MQTT_TOPIC": self.topic_input.text() or "#",  # Default to all topics if empty
                "WIFI_SSID": self.ssid_input.text(),
                "WIFI_PASSWORD": self.wifi_password_input.text()
            }
            
            # Update config values in memory
            config.MQTT_BROKER = settings["MQTT_BROKER"]
            config.MQTT_PORT = settings["MQTT_PORT"]
            config.MQTT_CLIENT_ID = settings["MQTT_CLIENT_ID"]
            config.MQTT_USERNAME = settings["MQTT_USERNAME"]
            config.MQTT_PASSWORD = settings["MQTT_PASSWORD"]
            config.MQTT_TOPIC = settings["MQTT_TOPIC"]
            config.WIFI_SSID = settings["WIFI_SSID"]
            config.WIFI_PASSWORD = settings["WIFI_PASSWORD"]
            
            # Emit signal with new settings
            self.connectionUpdated.emit(settings)
            self.accept()
        except Exception as e:
            print(f"Error saving connection settings: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving settings: {str(e)}"
            )