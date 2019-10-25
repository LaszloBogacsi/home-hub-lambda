import json

import boto3
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name


class RebuildIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name('rebuild')(handler_input)

    def handle(self, handler_input):
        lambda_client = boto3.client('lambda')
        params = {
            "FunctionName": 'home-hub-interaction-model-dev-lambda',
            "InvocationType": 'RequestResponse',
            "Payload": json.dumps(handler_input.request_envelope.request)
        }
        lambda_response = lambda_client.invoke(params)

        interaction_model_response: InteractionModelResponse = json.loads(lambda_response['Payload'].read().decode(), object_hook=to)
        if interaction_model_response.request_card_type != "None":
            return handler_input.response_builder.set_card(interaction_model_response.request_card_type).speak(interaction_model_response.message).response
        else:
            return handler_input.response_builder.speak(interaction_model_response.message).set_should_end_session(True).response


# TODO: make this generic
def to(obj):
    return InteractionModelResponse(obj['requestCardType'], obj['message'])


class InteractionModelResponse:
    request_card_type: str
    message: str

    def __init__(self, request_card_type, message) -> None:
        self.request_card_type = request_card_type
        self.message = message

