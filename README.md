# <img alt="logo" src="home_hub_logo.svg" height="48" width="48"><img alt="logo" src="amazon-lambda-logo.jpg" height="24" width="24"> Home Hub Lambda ![CircleCI](https://circleci.com/gh/LaszloBogacsi/home-hub-lambda.svg?style=svg&circle-token=ca35c76a87867566051f0b4541f0864dfdd3a318)
AWS lambda function to provide connection between Alexa and Cloud MQTT to message between a Raspberry Pi

deploy to AWS Lambda using `serverless`  

#### Deploy
```
sls deploy
```
To destroy the stack:
```
sls remove
```
configuration in `serverless.yaml`