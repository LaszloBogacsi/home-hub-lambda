# -*- coding: utf-8 -*-

import decimal
import json

import boto3
from boto3.dynamodb.conditions import Attr, Or

from mqtt.MqttClient import MqttClient


def handler(event, context):
    # TODO: Use the device return messages to update local postgres db to acknowledge state of devices. So that home-hub will reflect Alexa state.
    # TODO: Better Alexa response message composed of location + status
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html

    client = get_mqtt_client(get_connection_params(boto3.client('ssm')))
    device_info = extract_event_params(event)
    name = device_info.name
    print(name)
    name = "living room"
    get_devices_by_name(name)
    payload = payload_builder(device_info, get_id_by) # TODO: Create payload from returned items. Handle no items returned case, handle error case
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
    state = params.state
    # location = params["location"]
    light_name = params.name

    device_status = status[0] if state == "on" else status[1]
    # light_id = id_getter(location, light_name)
    # return "{\"status\":\"" + device_status + "\",\"relay_id\":\"" + light_id + "\"}"


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
    pass


class DeviceInfo:
    name: str
    state: str

    def __init__(self, name, state) -> None:
        self.name = name
        self.state = state


def extract_event_params(event) -> DeviceInfo:
    slots = event["request"]["intent"]["slots"]
    device_name = slots["name"]["value"]
    state = slots["state"]["value"]
    return DeviceInfo(device_name, state)


def get_devices_by_name(name: str):
    return get_from_dynamo(name)


def get_from_dynamo(name: str):
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = 'dev-devices'
    table = dynamodb.Table(table_name)

    fe = Or(Attr('name').eq(name), Attr("location").eq(name))
    pe = "#g_id, #d_id, #name, #is_group, #delay, #loc"
    ean = {"#g_id": "group_id", "#d_id": "device_id", "#name": "name", "#is_group": "is_group",  "#delay": 'delay', "#loc": "location"}

    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe,
        ExpressionAttributeNames=ean
    )

    for i in response['Items']:
        print(json.dumps(i, cls=DecimalEncoder))

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )

        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))
    print(response)
    # TODO: Handle multiple return properly, multiple items, and items with multiple device_ids.
    return response['Items']


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
