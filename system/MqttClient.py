from paho.mqtt import client as mqtt_client
import logging
import time

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

username = 'max'
password = 'public'

class MqttClient():
    broker = 'homeassistant.local'
    port = 1883
    baseTopic = "greenhouse/"
    client_id = None
    logger = logging.getLogger(__name__)

    client = None

    def __init__(self):
        print("MQTT init")
        self.mqttConnect()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect to MQTT broker, return code %d\n", rc)

    def on_disconnect(client, userdata, rc):
        print("MQTT Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            print("MQTT Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                print("Reconnected to MQTT broker successfully!")
                return
            except Exception as err:
                print("%s. MQTT Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        print("MQTT Reconnect failed after %s attempts. Exiting...", reconnect_count)

    def mqttConnect(self):
        # Set Connecting Client ID
        self.client = mqtt_client.Client(self.client_id)
        self.client.username_pw_set(username, password)
        # client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect_async(self.broker, self.port)
    
    def publish(self, topic, message):
        result = self.client.publish(self.baseTopic + topic, message)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send to topic `{self.baseTopic + topic}`")
        else:
            print(f"Failed to send message to topic {self.baseTopic + topic}")
