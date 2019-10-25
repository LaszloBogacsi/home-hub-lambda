import random
import time

import boto3
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, get_slot_value
from boto3.dynamodb.conditions import Or, Attr

from exceptions import SlotValueNotPresentException
from mqtt.MqttClient import MqttClient


class DeviceOnOffIntentHandler(AbstractRequestHandler):

    def __init__(self, mqtt_client: MqttClient) -> None:
        super().__init__()
        self.mqtt_client = mqtt_client

    def can_handle(self, handler_input):
        return is_intent_name('deviceOnOff')(handler_input)

    def handle(self, handler_input):
        device_info = extract_event_params(handler_input)

        devices_to_notify = flatten(get_devices_by_name(device_info.name))
        payloads = payload_builder(device_info, devices_to_notify)
        print(payloads)
        for payload in payloads:
            print(payload)
            self.mqtt_client.publish(topic="remote/switch/relay", payload=payload)
            time.sleep(0.5)
        self.mqtt_client.on_all_finished()
        if len(devices_to_notify) == 0:
            message = 'No device found'
            return handler_input.response_builder.speak(message).response

        return handler_input.response_builder.speak(get_positive_answer()).response


def get_positive_answer():
    return random.choice(["OK", "Sure", "Done", "As you wish", "Yepp"])


def payload_builder(params, devices_to_notify):
    state = params.state
    payloads = ["{\"status\":\"" + state + "\",\"device_id\":\"" + device['device_id'] + "\"}" for device in devices_to_notify]
    return payloads


def get_devices_by_name(name: str):
    return get_from_dynamo(name)


class DeviceInfo:
    name: str
    state: str

    def __init__(self, name, state) -> None:
        self.name = name
        self.state = state


def extract_event_params(handler_input) -> DeviceInfo:
    device_name = get_slot_value(handler_input, 'name')
    state = get_slot_value(handler_input, 'state')
    print("device info: ", device_name, state)

    if device_name is not None and state is not None:
        return DeviceInfo(device_name.lower(), state.upper())
    else:
        raise SlotValueNotPresentException


def flatten(devices: []):
    flattened_devices = []
    for device in devices:
        print(device)
        ids = device['device_id'].split(',')
        for id in ids:
            new_dev = device.copy()
            new_dev.update({'device_id': id})
            flattened_devices.append(new_dev)

    return flattened_devices


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

