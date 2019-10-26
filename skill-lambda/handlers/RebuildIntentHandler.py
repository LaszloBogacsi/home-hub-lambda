import decimal
import importlib
import json
import logging
from datetime import datetime

import boto3
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_model.ui import Card

from handlers.reponse.InteractionModelResponse import InteractionModelResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RebuildIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name('rebuild')(handler_input)

    def handle(self, handler_input):
        lambda_client = boto3.client('lambda')
        logger.info("invoking lambda ...")
        params = {
            "FunctionName": 'home-hub-interaction-model-dev-lambda',
            "InvocationType": 'RequestResponse',
            "Payload": json.dumps(handler_input.request_envelope.to_dict(), default=default_conv)
        }
        lambda_response = lambda_client.invoke(**params)

        interaction_model_response: InteractionModelResponse = json.loads(lambda_response['Payload'].read().decode(), object_hook=to_response("InteractionModelResponse"))
        if interaction_model_response.request_card_type != "None":
            logger.info("invoking lambda ...")

            return handler_input.response_builder.set_card(Card(interaction_model_response.request_card_type)).speak(interaction_model_response.message).response
        else:
            return handler_input.response_builder.speak(interaction_model_response.message).set_should_end_session(True).response


def default_conv(o):
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, decimal.Decimal):
        dec = decimal.Decimal(o)
        return float(dec)
    return o.__dict__


def to_response(klass):
    module = importlib.import_module("reponse")
    class_ = getattr(module, "{}".format(klass))

    def conv(obj):
        class_(**obj)
    return conv
