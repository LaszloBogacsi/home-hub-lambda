# -*- coding: utf-8 -*-

import boto3 as boto3

from mqtt.mqtt_client import MqttClient


def handler(event, context):

    # TODO: create Group intent
    # TODO: create Single device intent
    # TODO: Save group names to dynamo and read from there
    # TODO: Save Single device names to dynamo and read from there
    # TODO: Save Location names to dynamo and read from there
    # TODO: Use the device return messages to update local postgres db to acknowledge state of devices. So that home-hub will reflect Alexa state.
    # TODO: Better Alexa response message composed of location + status
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html

    client = get_mqtt_client(get_connection_params(boto3.client('ssm')))
    payload = payload_builder(extract_event_params(event), get_id_by)
    print(payload)
    client.publish(topic="remote/switch/relay", payload=payload)
    return {
        "version": "string",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": 'OK',
                "playBehavior": "REPLACE_ENQUEUED"
            },
            "shouldEndSession": "true"
        }
    }


devices = ('table lamp', 'standing lamp', 'fairy lights', 'cupboard lights')
locations = ('living room', 'kitchen', 'bed room')
status = ('ON', 'OFF')
location_id_map = [
    {'location': locations[0], 'name': devices[0], 'id': '1'},
    {'location': locations[0], 'name': devices[2], 'id': '2'}
]


def get_id_by(location, light_name):
    return next(x for x in location_id_map if x.get('location') == location and x.get('name') == light_name).get('id')


def payload_builder(params, id_getter):
    state = params["state"]
    location = params["location"]
    light_name = params["light_name"]

    device_status = status[0] if state == "on" else status[1]
    light_id = id_getter(location, light_name)
    return "{\"status\":\"" + device_status + "\",\"relay_id\":\"" + light_id + "\"}"


def get_connection_params(ssm):
    password = ssm.get_parameter(Name='/homehub/cloudmqtt/password', WithDecryption=True)['Parameter']['Value']
    username = ssm.get_parameter(Name='/homehub/cloudmqtt/username', WithDecryption=True)['Parameter']['Value']
    host = ssm.get_parameter(Name='/homehub/cloudmqtt/host')['Parameter']['Value']
    port = int(ssm.get_parameter(Name='/homehub/cloudmqtt/host/port')['Parameter']['Value'])
    return {
        "password": password,
        "username": username,
        "host": host,
        "port": port
    }


def get_mqtt_client(conn_params):
    return MqttClient(conn_params["username"], conn_params["password"], conn_params["host"], conn_params["port"])


def extract_event_params(event):
    slots = event["request"]["intent"]["slots"]
    location = slots["location"]["value"]
    light_name = slots["light_name"]["value"]
    state = slots["state"]["value"]
    return {
        "location": location,
        "light_name": light_name,
        "state": state
    }
