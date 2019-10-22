import json
import urllib.request

import boto3


def handle(event, context):
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html
    # TODO: https://developer.amazon.com/settings/console/securityprofile/web-settings/view.html?identityAppFamilyId=amzn1.application.a7067441a49e4524911677c1c23bf8a3
    #       to use the SMAPI need to implement oauth2.0 with amazon login

    skill_id = "amzn1.ask.skill.fa5e222d-7762-4db6-8161-4be6648262c4"
    stage = "development"
    locale = "en-US"

    skill_invocation_name = "home hub"
    api_access_token = event['context']['System']['apiAccessToken']
    api_endpoint = 'https://api.amazonalexa.com'
    scope = 'alexa::ask:models:readwrite'
    url = "{}/v1/skills/{}/stages/{}/interactionModel/locales/{}".format(api_endpoint, skill_id, stage, locale)

    def generate_device_name(name: str):
        return {
            "name": {
                "value": name
            }
        }

    device_names = [generate_device_name(name) for name in to_list(get_all_names_and_locations_from_dynamo())]

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
    req = urllib.request.Request(url, interaction_model_schema, {"Authorization": "Bearer {}".format(api_access_token)}, method='PUT')
    response = urllib.request.urlopen(req)
    html = response.read()
    json_obj = json.loads(html)
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
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


if __name__ == '__main__':
    print('hi')
