import boto3 as boto3
import paho.mqtt.client as mqtt

devices = ('table lamp', 'standing lamp', 'fairy lights', 'cupboard lights')
locations = ('living room', 'kitchen', 'bed room')
location_id_map = [
    {'location': locations[0], 'name': devices[0], 'id': '1'},
    {'location': locations[0], 'name': devices[1], 'id': '2'}
]


def get_id_by(location, light_name):
    return next(x for x in location_id_map if x.get('location') == location and x.get('name') == light_name).get('id')


def payload_builder(location, light_name, state):
    status = "ON" if state == "on" else "OFF"

    light_id = get_id_by(location, light_name)
    return "{\"status\":\"" + status + "\",\"relay_id\":\"" + light_id + "\"}"


def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    password = ssm.get_parameter(Name='/homehub/cloudmqtt/password', WithDecryption=True)['Parameter']['Value']
    username = ssm.get_parameter(Name='/homehub/cloudmqtt/username', WithDecryption=True)['Parameter']['Value']
    host = ssm.get_parameter(Name='/homehub/cloudmqtt/host')['Parameter']['Value']
    port = ssm.get_parameter(Name='/homehub/cloudmqtt/host/port')['Parameter']['Value']
    client = MqttClient(username, password, host, port)
    slots = event["request"]["intent"]["slots"]
    location = slots["location"]["value"]
    light_name = slots["light_name"]["value"]
    state = slots["state"]["value"]
    print(location + ' ' + light_name + ' ' + state)
    payload = payload_builder(location, light_name, state)
    print(payload)
    topic = "remote/switch/relay"
    client.publish(topic, payload)
    return {
        "version": "string",
        "sessionAttributes": {"key": "value"},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": 'OK',
                "playBehavior": "REPLACE_ENQUEUED"
            },
            "shouldEndSession": "true"
        }
    }


class MqttClient:

    def __init__(self, username, password, host, port):
        self.latest_message = ""

        client = mqtt.Client('Home hub AWS Lambda')
        self.client = client
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.username_pw_set(username, password)
        try:
            client.connect(host, port)
            client.loop_start()
        except:
            print("connection to mqtt client on " + host + " has failed")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK Returned code=", rc)
        else:
            print("Bad connection Returned code=", rc)

    def on_message(self, client, userdata, message):
        pass

    def on_publish(self, client, userdata, mid):
        self.client.disconnect()

    def publish(self, topic, payload):
        self.client.publish(topic=topic, payload=payload)
