import json


def handle(event, context):
    # TODO: https://developer.amazon.com/docs/smapi/interaction-model-operations.html#update-interaction-model saving/updating a group name or light name would feed back to
    #        alexas interaction model (teaching the model), https://developer.amazon.com/docs/smapi/interaction-model-schema.html

    url = "PUT /v1/skills/{skillId}/stages/{stage}/interactionModel/locales/{locale}"
    skill_invocation_name = "home hub"
    generate_device_names = {
        "name": {
            "value": "Mercury"
        }
    }

    get_device_names = [generate_device_names]

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
                        "values": get_device_names
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
                                "validations": [ ]
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

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
