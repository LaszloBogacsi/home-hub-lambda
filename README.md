# Home Hub Lambda

AWS lambda function to provide connection between Alexa and Cloud MQTT to message between a Raspberry Pi


zip the virtual env site-packages folder
add the function python code to the zip

deploy to AWS Lambda
`aws lambda update-function-code --function-name lambda_alexa_mqtt --zip-file fileb://function.zip`
 