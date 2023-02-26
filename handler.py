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

def handleS3Upload(event, context):
    bucket = os.environ['JUPYTER_NOTEBOOK_SUBMISSION_BUCKET']
    region_name = os.environ['REGION_NAME']

    filesUploaded = event['Records']

    for file in filesUploaded:
        fileName = file["s3"]["object"]["key"]
        fileSize = file["s3"]["object"]["size"];
        print(fileName)
        print(fileSize)

    return(fileName)