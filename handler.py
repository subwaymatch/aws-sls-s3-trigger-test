import json
import boto3
import os

def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    print(body)

    return {"statusCode": 200, "body": json.dumps(body)}