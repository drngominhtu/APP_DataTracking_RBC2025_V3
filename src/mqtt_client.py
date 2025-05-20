import paho.mqtt.client as mqtt
from PyQt5.QtCore import QObject, pyqtSignal
import json
from config import MQTT_USERNAME, MQTT_PASSWORD


class MqttClient(QObject):
    message_received = pyqtSignal(str, str)  # topic, message
    connection_changed = pyqtSignal(bool)    # connected status
    topic_detected = pyqtSignal(str)         # new topic detected
    
    def __init__(self, broker, port, message_callback=None):
        super().__init__()
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.message_callback = message_callback
        self.subscribed_topics = set()
        self.detected_topics = set()
        
        # Đặt thông tin xác thực từ config
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def subscribe(self, topic):
        result = self.client.subscribe(topic)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            self.subscribed_topics.add(topic)
            print(f"Subscribed to {topic}")
            return True
        else:
            print(f"Failed to subscribe to {topic}")
            return False
            
    def unsubscribe(self, topic):
        if topic == "#":
            # Don't allow unsubscribing from all topics
            return False
            
        result = self.client.unsubscribe(topic)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            self.subscribed_topics.discard(topic)
            return True
        return False
        
    def publish(self, topic, message):
        self.client.publish(topic, message)
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            self.connection_changed.emit(True)
            
            # Resubscribe to all topics
            for topic in self.subscribed_topics:
                client.subscribe(topic)
                
            # Subscribe to default topic if not already subscribed
            if not self.subscribed_topics:
                from config import MQTT_TOPIC
                client.subscribe(MQTT_TOPIC)
                self.subscribed_topics.add(MQTT_TOPIC)
                
        else:
            print(f"Failed to connect to MQTT broker with code: {rc}")
            self.connection_changed.emit(False)
            
    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker")
        self.connection_changed.emit(False)
        
    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode("utf-8")
        
        # Add to detected topics
        if topic not in self.detected_topics:
            self.detected_topics.add(topic)
            self.topic_detected.emit(topic)
        
        print(f"Message received: {topic} -> {payload}")
        
        # Try to parse as JSON
        try:
            json_data = json.loads(payload)
            if isinstance(json_data, dict):
                # For each key in the JSON, emit as if it were a separate topic
                for key, value in json_data.items():
                    subtopic = f"{topic}/{key}"
                    if subtopic not in self.detected_topics:
                        self.detected_topics.add(subtopic)
                        self.topic_detected.emit(subtopic)
        except json.JSONDecodeError:
            # Not JSON, continue with normal processing
            pass
        
        self.message_received.emit(topic, payload)
        
        if self.message_callback:
            self.message_callback(client, userdata, message)
            
    def get_detected_topics(self):
        return list(self.detected_topics)
        
    def get_subscribed_topics(self):
        return list(self.subscribed_topics)