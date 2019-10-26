import uuid

import paho.mqtt.client as mqtt


class MqttClient:

    def __init__(self, username, password, host, port):
        self.latest_message = ""

        client = mqtt.Client('Home hub AWS Lambda-{}'.format(uuid.uuid4()))
        self.client = client
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(username, password)
        try:
            client.connect(host=host, port=port)
            client.loop_start()
        except Exception as e:
            print("connection to mqtt client on " + host + " has failed, reason: " + str(e))

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK Returned code=", rc)
        else:
            print("Bad connection Returned code=", rc)

    def on_message(self, client, userdata, message):
        pass

    def on_all_finished(self):
        self.client.disconnect()

    def publish(self, topic, payload):
        self.client.publish(topic=topic, payload=payload)
