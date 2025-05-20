from PyQt5 import QtWidgets, QtGui, QtCore
import json
import os

class ConnectionSettingsDialog(QtWidgets.QDialog):
    """Dialog for MQTT connection settings"""
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Settings")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Store current settings
        self.current_settings = current_settings or {}
        
        # Create layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create form layout for settings
        form_layout = QtWidgets.QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Connection name
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setText(self.current_settings.get("name", "Default Connection"))
        form_layout.addRow("Connection Name:", self.name_input)
        
        # MQTT Broker settings group
        self.broker_group = QtWidgets.QGroupBox("MQTT Broker")
        broker_layout = QtWidgets.QFormLayout()
        
        # Protocol selection
        self.protocol_combo = QtWidgets.QComboBox()
        self.protocol_combo.addItems(["mqtt://", "mqtts://"])
        current_protocol = self.current_settings.get("protocol", "mqtt://")
        self.protocol_combo.setCurrentText(current_protocol)
        broker_layout.addRow("Protocol:", self.protocol_combo)
        
        # Broker address
        self.broker_input = QtWidgets.QLineEdit()
        self.broker_input.setText(self.current_settings.get("broker", "192.168.5.1"))
        broker_layout.addRow("Broker:", self.broker_input)
        
        # Port
        self.port_input = QtWidgets.QSpinBox()
        self.port_input.setMinimum(1)
        self.port_input.setMaximum(65535)
        self.port_input.setValue(self.current_settings.get("port", 1883))
        broker_layout.addRow("Port:", self.port_input)
        
        # Set layout for broker group
        self.broker_group.setLayout(broker_layout)
        
        # Authentication group
        self.auth_group = QtWidgets.QGroupBox("Authentication")
        auth_layout = QtWidgets.QFormLayout()
        
        # Username
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setText(self.current_settings.get("username", ""))
        auth_layout.addRow("Username:", self.username_input)
        
        # Password
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setText(self.current_settings.get("password", ""))
        auth_layout.addRow("Password:", self.password_input)
        
        # Show password checkbox
        self.show_password = QtWidgets.QCheckBox("Show Password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        auth_layout.addRow("", self.show_password)
        
        # Set layout for auth group
        self.auth_group.setLayout(auth_layout)
        
        # Advanced options group
        self.advanced_group = QtWidgets.QGroupBox("Advanced Options")
        advanced_layout = QtWidgets.QFormLayout()
        
        # Client ID
        self.client_id_input = QtWidgets.QLineEdit()
        self.client_id_input.setText(self.current_settings.get("client_id", f"mqtt_monitor_{os.getpid()}"))
        advanced_layout.addRow("Client ID:", self.client_id_input)
        
        # Keep alive
        self.keep_alive_input = QtWidgets.QSpinBox()
        self.keep_alive_input.setMinimum(5)
        self.keep_alive_input.setMaximum(3600)
        self.keep_alive_input.setValue(self.current_settings.get("keep_alive", 60))
        advanced_layout.addRow("Keep Alive (s):", self.keep_alive_input)
        
        # QoS
        self.qos_combo = QtWidgets.QComboBox()
        self.qos_combo.addItems(["0 - At most once", "1 - At least once", "2 - Exactly once"])
        self.qos_combo.setCurrentIndex(self.current_settings.get("qos", 0))
        advanced_layout.addRow("QoS:", self.qos_combo)
        
        # Default topic
        self.default_topic_input = QtWidgets.QLineEdit()
        self.default_topic_input.setText(self.current_settings.get("default_topic", "#"))
        advanced_layout.addRow("Default Topic:", self.default_topic_input)
        
        # SSL options
        self.use_ssl = QtWidgets.QCheckBox("Use SSL/TLS")
        self.use_ssl.setChecked(self.current_settings.get("use_ssl", False))
        self.use_ssl.stateChanged.connect(self.toggle_ssl_options)
        advanced_layout.addRow("", self.use_ssl)
        
        # SSL options container - initially hidden
        self.ssl_container = QtWidgets.QWidget()
        ssl_layout = QtWidgets.QFormLayout()
        ssl_layout.setContentsMargins(0, 0, 0, 0)
        
        # CA file
        self.ca_file_input = QtWidgets.QLineEdit()
        self.ca_file_input.setText(self.current_settings.get("ca_file", ""))
        ca_button = QtWidgets.QPushButton("Browse...")
        ca_button.clicked.connect(lambda: self.browse_file(self.ca_file_input))
        ca_layout = QtWidgets.QHBoxLayout()
        ca_layout.addWidget(self.ca_file_input)
        ca_layout.addWidget(ca_button)
        ssl_layout.addRow("CA File:", ca_layout)
        
        # Client cert
        self.cert_file_input = QtWidgets.QLineEdit()
        self.cert_file_input.setText(self.current_settings.get("cert_file", ""))
        cert_button = QtWidgets.QPushButton("Browse...")
        cert_button.clicked.connect(lambda: self.browse_file(self.cert_file_input))
        cert_layout = QtWidgets.QHBoxLayout()
        cert_layout.addWidget(self.cert_file_input)
        cert_layout.addWidget(cert_button)
        ssl_layout.addRow("Client Cert:", cert_layout)
        
        # Client key
        self.key_file_input = QtWidgets.QLineEdit()
        self.key_file_input.setText(self.current_settings.get("key_file", ""))
        key_button = QtWidgets.QPushButton("Browse...")
        key_button.clicked.connect(lambda: self.browse_file(self.key_file_input))
        key_layout = QtWidgets.QHBoxLayout()
        key_layout.addWidget(self.key_file_input)
        key_layout.addWidget(key_button)
        ssl_layout.addRow("Client Key:", key_layout)
        
        self.ssl_container.setLayout(ssl_layout)
        advanced_layout.addRow("", self.ssl_container)
        
        # Set visibility based on SSL checkbox
        self.ssl_container.setVisible(self.use_ssl.isChecked())
        
        # Set layout for advanced group
        self.advanced_group.setLayout(advanced_layout)
        
        # Add all elements to main layout
        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.broker_group)
        self.layout.addWidget(self.auth_group)
        self.layout.addWidget(self.advanced_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        # Test connection button
        self.test_button = QtWidgets.QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Save button
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        # Cancel button
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
    
    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == QtCore.Qt.Checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
    
    def toggle_ssl_options(self, state):
        """Toggle SSL options visibility"""
        self.ssl_container.setVisible(state == QtCore.Qt.Checked)
        
        # Adjust port if SSL is toggled
        if state == QtCore.Qt.Checked and self.port_input.value() == 1883:
            self.port_input.setValue(8883)  # Default SSL port
        elif state == QtCore.Qt.Unchecked and self.port_input.value() == 8883:
            self.port_input.setValue(1883)  # Default non-SSL port
    
    def browse_file(self, target_input):
        """Open file dialog and set selected file to target input"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        if file_path:
            target_input.setText(file_path)
    
    def test_connection(self):
        """Test the connection with current settings"""
        try:
            import paho.mqtt.client as mqtt
            import time
            
            # Create client with clean session
            client = mqtt.Client(client_id=self.client_id_input.text())
            
            # Set credentials if provided
            if self.username_input.text():
                client.username_pw_set(
                    self.username_input.text(),
                    self.password_input.text()
                )
            
            # Configure SSL if enabled
            if self.use_ssl.isChecked():
                client.tls_set(
                    ca_certs=self.ca_file_input.text() or None,
                    certfile=self.cert_file_input.text() or None,
                    keyfile=self.key_file_input.text() or None
                )
            
            # Set up connection timeout
            connected = [False]
            
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    connected[0] = True
                else:
                    # Connection failed
                    connected[0] = False
            
            client.on_connect = on_connect
            
            # Connect with timeout
            client.connect_async(
                self.broker_input.text(), 
                self.port_input.value(),
                keepalive=self.keep_alive_input.value()
            )
            client.loop_start()
            
            # Wait for connection or timeout
            timeout = 5  # seconds
            start_time = time.time()
            while not connected[0] and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # Stop the client
            client.loop_stop()
            client.disconnect()
            
            # Show result
            if connected[0]:
                QtWidgets.QMessageBox.information(
                    self, 
                    "Connection Test", 
                    f"Successfully connected to {self.broker_input.text()}:{self.port_input.value()}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Connection Test", 
                    f"Failed to connect to {self.broker_input.text()}:{self.port_input.value()}"
                )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Connection Test Error", 
                f"Error testing connection: {str(e)}"
            )
    
    def get_settings(self):
        """Return the current settings as a dictionary"""
        settings = {
            "name": self.name_input.text(),
            "protocol": self.protocol_combo.currentText(),
            "broker": self.broker_input.text(),
            "port": self.port_input.value(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "client_id": self.client_id_input.text(),
            "keep_alive": self.keep_alive_input.value(),
            "qos": self.qos_combo.currentIndex(),
            "default_topic": self.default_topic_input.text(),
            "use_ssl": self.use_ssl.isChecked(),
            "ca_file": self.ca_file_input.text(),
            "cert_file": self.cert_file_input.text(),
            "key_file": self.key_file_input.text(),
        }
        return settings