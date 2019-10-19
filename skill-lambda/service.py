import decimal
import json
import random

import boto3
from boto3.dynamodb.conditions import Attr, Or

from mqtt.MqttClient import MqttClient


def handler(event, context):
    # TODO: Use the device return messages to update local postgres db to acknowledge state of devices. So that home-hub will reflect Alexa state.
    # TODO: Better Alexa response message composed of location + status
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html
    try:
        client = get_mqtt_client(get_connection_params(boto3.client('ssm')))
        device_info = extract_event_params(event)
        name = device_info.name
        devices_to_notify = flatten(get_devices_by_name(name))
        payloads = payload_builder(device_info, devices_to_notify)
        print(payloads)
        for payload in payloads:
            print(payload)
            client.publish(topic="remote/switch/relay", payload=payload)

        if len(devices_to_notify) == 0:
            return response('No device found')

        return response(get_positive_answer())

    except Exception as e:
        return response(e)


def get_positive_answer():
    return random.choice(["OK", "Sure", "Done", "As you wish", "Yepp"])


def response(text):
    return {
        "version": "string",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text,
                "playBehavior": "REPLACE_ENQUEUED"
            },
            "shouldEndSession": "true"
        }
    }


def payload_builder(params, devices_to_notify):
    state = params.state
    payloads = ["{\"status\":\"" + state + "\",\"relay_id\":\"" + device['device_id'] + "\"}" for device in devices_to_notify]
    return payloads


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
    print(event)
    slots = event["request"]["intent"]["slots"]
    device_name = slots["name"]["value"]
    state = slots["state"]["value"]
    if state:
        state = state.upper()
    return DeviceInfo(device_name, state)


def get_devices_by_name(name: str):
    return get_from_dynamo(name)


def get_from_dynamo(name: str):
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = 'dev-devices'
    table = dynamodb.Table(table_name)

    fe = Or(Attr('name').eq(name), Attr("location").eq(name))
    pe = "#g_id, #d_id, #name, #is_group, #delay, #loc"
    ean = {"#g_id": "group_id", "#d_id": "device_id", "#name": "name", "#is_group": "is_group", "#delay": 'delay', "#loc": "location"}
    all_responses = []

    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe,
        ExpressionAttributeNames=ean
    )

    for i in response['Items']:
        all_responses.append(i)

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        for i in response['Items']:
            all_responses.append(i)
    print(all_responses)
    return all_responses


def flatten(devices: [object]):
    flattened_devices = []
    for device in devices:
        print(device)
        ids = device['device_id'].split(',')
        for id in ids:
            new_dev = device.copy()
            new_dev.update({'device_id': id})
            flattened_devices.append(new_dev)

    return flattened_devices


if __name__ == "__main__":
    test_devices = [
        {"device_id": "502,503,504", "is_group": True, "location": "living room", "name": "Some name of this lamp", "group_id": "502", "delay": 0},
        {"device_id": "501", "is_group": False, "location": "living room", "name": "Some name of this lamp", "group_id": "501", "delay": 0}
    ]
    # devs = flatten(test_devices)
    # payload_builder(DeviceInfo('living room', 'OFF'), devs)
