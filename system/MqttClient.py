from paho.mqtt import client as mqtt_client
import logging
import time

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 10
MAX_RECONNECT_DELAY = 60

class MqttClient():
    broker = None
    port = None
    baseTopic = "greenhouse/"
    client_id = None
    username = None
    password = None
    logger = logging.getLogger(__name__)
    connected = False

    client = None

    def __init__(self, config):
        self.broker = config["broker"]
        self.port = int(config["port"])
        self.client_id = config["client_id"]
        self.username = config["user"]
        self.password = config["pw"]
        print("Connecting to MQTT broker: " + self.broker)
        self.mqttConnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.logger.info("connected to MQTT broker")
            self.connected = True
        else:
            self.logger.info("failed to connect to MQTT broker, return code %d\n")
            print("Failed to connect to MQTT broker, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        print("MQTT Disconnected with result code: %s", rc)
        self.logger.info("MQTT Disconnected with result code: %s")
        self.connected = False
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            print("MQTT Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                self.logger.info("reconnected to MQTT broker successfully")
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
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect_async(self.broker, self.port)
        self.client.loop_start()
    
    def publish(self, topic, message):
        
        result = self.client.publish(self.baseTopic + topic, message, 0)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            self.logger.info(f"send to topic `{self.baseTopic + topic}`")
            #print(f"Send to topic `{self.baseTopic + topic}`")
        else:
            self.logger.info(f"failed to send message to topic {self.baseTopic + topic} - {status}")
            #print(f"Failed to send message to topic {self.baseTopic + topic} - {status}")
