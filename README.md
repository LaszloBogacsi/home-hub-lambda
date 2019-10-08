# <img alt="logo" src="home_hub_logo.svg" height="48" width="48"><img alt="logo" src="amazon-lambda-logo.jpg" height="48" width="48"> Home Hub Lambda

AWS lambda function to provide connection between Alexa and Cloud MQTT to message between a Raspberry Pi

deploy to AWS Lambda using `python-lambda`  
python-lambda takes care of installing and packaging the dependencies and deploy to AWS Lambda or S3.

#### Deploy
create `requirements.txt` 
```
pipenv run pip freeze > requirements.txt
```
```
lambda deploy
```
windows: 
```
pipenv run python C:\Users\<USER>\.virtualenvs\<PROJECT_FOLDER>\Scripts\lambda deploy
```  
configuration in `config.yaml`

#### Test (*locally*)
```
lambda invoke
``` 
calls the lambda funciton with input from `event.json`