import json
import urllib.request

import boto3


def handle(event, context):
    skill_id = "amzn1.ask.skill.fa5e222d-7762-4db6-8161-4be6648262c4"
    stage = "development"
    locale = "en-GB"
    skill_invocation_name = "home hub"
    api_endpoint = 'https://api.amazonalexa.com'
    url = "{}/v1/skills/{}/stages/{}/interactionModel/locales/{}".format(api_endpoint, skill_id, stage, locale)
    access_token = event['context']['System']['user'].get('accessToken', None)

    if access_token is None:
        print("requesting account linking...")
        return card_requesting_account_linking()

    def generate_device_name(name: str):
        return {
            "name": {
                "value": name
            }
        }
    print('getting device names')
    device_names = [generate_device_name(name) for name in to_list(get_all_names_and_locations_from_dynamo())]
    print("got {} devices".format(len(device_names)))
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
                        "name": "GetTravelTime",
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
    req = urllib.request.Request(url, interaction_model_schema, {"Authorization": "Bearer {}".format(access_token)}, method='PUT')
    response = urllib.request.urlopen(req)
    html = response.read()
    json_obj = json.loads(html)
    print(json_obj)
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Rebuild complete",
                "playBehavior": "REPLACE_ENQUEUED"
            },
            "shouldEndSession": "true"
        }
    }

    return response


def get_all_names_and_locations_from_dynamo():
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = 'dev-devices'
    table = dynamodb.Table(table_name)

    pe = "#name, #loc"
    ean = {"#name": "name", "#loc": "location"}
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
    print(all_responses)
    return all_responses


def to_list(response):
    return list(set(res for res in response for res in res.values() if res != 'None'))


def card_requesting_account_linking():
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Please authenticate with you amazon account to use this feature, for further information please visit your alexa app."
            },
            "card": {
                "type" : "LinkAccount"
            },
            "shouldEndSession": "true"
        }
    }


if __name__ == '__main__':
    print('hi')
