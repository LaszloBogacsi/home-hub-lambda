import json
import os
import urllib.request
import logging
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle(event, context):
    try:
        logger.debug(event)
        skill_id = event['context']['system']['application']['application_id']
        stage = "development"
        locale = "en-GB"
        skill_invocation_name = "home hub"
        api_endpoint = 'https://api.amazonalexa.com'
        url = "{}/v1/skills/{}/stages/{}/interactionModel/locales/{}".format(api_endpoint, skill_id, stage, locale)
        access_token = event['context']['system']['user'].get('access_token', None)

        if access_token is None:
            logger.info("requesting account linking...")
            return lambda_response("LinkAccount", "Please authenticate with you amazon account to use this feature, for further information please visit your alexa app.")

        logger.info("getting device names")

        device_names = [generate_device_name(name) for name in to_list_of_values(get_all_names_and_locations_from_dynamo())]
        logger.info("got {} devices".format(len(device_names)))
        interaction_model_schema = generate_interaction_model_schema(device_names, skill_invocation_name)
        payload_str = json.dumps(interaction_model_schema)
        req = urllib.request.Request(url, payload_str.encode(), {"Authorization": "Bearer {}".format(access_token)}, method='PUT')
        response = urllib.request.urlopen(req)
        html = response.read()
        logger.info(json.loads(html))

        return lambda_response()
    except Exception as e:
        logger.error(e, exc_info=True)
        return lambda_response(message="An error occurred during rebuilding")


def generate_interaction_model_schema(device_names, skill_invocation_name):
    interaction_model_schema = {
        "interactionModel": {
            "languageModel": {
                "invocationName": skill_invocation_name,
                "intents": [
                    {
                        "name": "AMAZON.CancelIntent",
                        "samples": []
                    },
                    {
                        "name": "AMAZON.HelpIntent",
                        "samples": []
                    },
                    {
                        "name": "AMAZON.StopIntent",
                        "samples": []
                    },
                    {
                        "name": "deviceOnOff",
                        "slots": [
                            {
                                "name": "name",
                                "type": "DeviceName",
                                "samples": []
                            },
                            {
                                "name": "state",
                                "type": "SwitchState",
                                "samples": []
                            }
                        ],
                        "samples": [
                            "turn the {name} {state}",
                            "turn {name} {state}",
                            "turn {state} {name}",
                        ]
                    },
                    {
                        "name": "rebuild",
                        "slots": [],
                        "samples": [
                            "rebuild",
                        ]
                    }
                ],
                "types": [
                    {
                        "name": "DeviceName",
                        "values": device_names
                    },
                    {
                        "name": "SwitchState",
                        "values": [
                            {
                                "name": {
                                    "value": "on"
                                }
                            },
                            {
                                "name": {
                                    "value": "off"
                                }
                            },
                        ]
                    }
                ]
            },
            "dialog": {
                "intents": [
                    {
                        "name": "deviceOnOff",
                        "confirmationRequired": False,
                        "prompts": {},
                        "slots": [
                            {
                                "name": "name",
                                "type": "DeviceName",
                                "confirmationRequired": False,
                                "elicitationRequired": True,
                                "prompts": {
                                    "elicitation": "Elicit.Intent-deviceOnOff.IntentSlot-name"
                                },
                                "validations": []
                            },
                            {
                                "name": "state",
                                "type": "SwitchState",
                                "confirmationRequired": False,
                                "elicitationRequired": True,
                                "prompts": {
                                    "elicitation": "Elicit.Intent-deviceOnOff.IntentSlot-state"
                                }
                            }
                        ]
                    }
                ],
                "delegationStrategy": "ALWAYS"
            },
            "prompts": [
                {
                    "id": "Elicit.Intent-deviceOnOff.IntentSlot-name",
                    "variations": [
                        {
                            "type": "PlainText",
                            "value": "For what device or group name?"
                        }
                    ]
                },
                {
                    "id": "Elicit.Intent-deviceOnOff.IntentSlot-state",
                    "variations": [
                        {
                            "type": "PlainText",
                            "value": "Do you want it on or off?"
                        }
                    ]
                }
            ]

        }
    }
    return interaction_model_schema


def lambda_response(card_type="None", message="Rebuild complete"):
    return {
        "requestCardType": card_type,
        "message": message
    }


def get_all_names_and_locations_from_dynamo():
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = os.environ['TableName']
    table = dynamodb.Table(table_name)

    pe = "#name, #loc"
    ean = {"#name": "name", "#loc": "location"}
    return scan_table(ean, pe, table)


def scan_table(ean, pe, table) -> []:
    all_responses = []
    response = table.scan(
        ProjectionExpression=pe,
        ExpressionAttributeNames=ean
    )
    for i in response['Items']:
        all_responses.append(i)
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
            ExpressionAttributeNames=ean,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        for i in response['Items']:
            all_responses.append(i)
    logger.debug(all_responses)
    return all_responses


def to_list_of_values(response):
    return list(set(res for res in response for res in res.values() if res != 'None'))


def generate_device_name(name: str):
    return { "name": { "value": name } }