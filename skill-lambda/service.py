import boto3
from ask_sdk_core.skill_builder import SkillBuilder

from exceptions import SlotValueNotPresentException, CatchAllExceptionHandler
from handlers import RebuildIntentHandler, DeviceOnOffIntentHandler
from mqtt.MqttClient import MqttClient

# TODO: CREATE aws service account for circle ci deployments

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


mqtt_client = get_mqtt_client(get_connection_params(boto3.client('ssm')))
sb = SkillBuilder()

# register request handlers
sb.add_request_handler(RebuildIntentHandler())
sb.add_request_handler(DeviceOnOffIntentHandler(mqtt_client))

# register exception handlers
sb.add_exception_handler(SlotValueNotPresentException())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
