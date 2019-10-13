# -*- coding: utf-8 -*-

import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from mqtt.mqtt_client import MqttClient


def handler(event, context):

    # TODO: Save group names to dynamo and read from there
    # TODO: Save Single device names to dynamo and read from there
    # TODO: Save Location names to dynamo and read from there
    # TODO: Use the device return messages to update local postgres db to acknowledge state of devices. So that home-hub will reflect Alexa state.
    # TODO: Better Alexa response message composed of location + status
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html

    # client = get_mqtt_client(get_connection_params(boto3.client('ssm')))
    print(extract_event_params(event))
    name = 'living room'
    get_devices_by_name(name)
    # payload = payload_builder(extract_event_params(event), get_id_by)
    # print(payload)
    # client.publish(topic="remote/switch/relay", payload=payload)
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
    device_name = slots["name"]["value"]
    state = slots["state"]["value"]
    return {
        "light_name": device_name,
        "state": state
    }


def get_devices_by_name(name: str):
    get_from_dynamo(name)


def get_from_dynamo(name: str):
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = 'dev-devices'

    table = dynamodb.Table(table_name)
    try:
        response1 = table.query(
            KeyConditionExpression=Key('name').eq(name)
        )
        response2 = table.query(
            AttributeConditionExpression=Key('location').eq(name)
        )


    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("GetItem succeeded:")
        for i in response1['Items']:
            print(json.dumps(i, indent=4, cls=DecimalEncoder))
        for i in response2['Items']:
            print(json.dumps(i, indent=4, cls=DecimalEncoder))



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)