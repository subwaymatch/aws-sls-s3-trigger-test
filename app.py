import json
import os
import pandas as pd

def get_tomatoes(event, context):
    tomatoes = [{"name": "Red Tomato", "price": "30 Rs"},
            {"name": "Yellow Tomato", "price": "35 Rs"},
            {"name": "Small Tomato", "price": "20 Rs"}]
    tomatoesList = {"tomatoes": tomatoes}
    response = {"statusCode": 200, "body": json.dumps(tomatoesList)}

    print(response)

    bucket = os.environ['JUPYTER_NOTEBOOK_SUBMISSION_BUCKET']
    region_name = os.environ['REGION_NAME']

    filesUploaded = event['Records']

    print(pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['A', 'B', 'C']
    }))

    for file in filesUploaded:
        fileName = file["s3"]["object"]["key"]
        fileSize = file["s3"]["object"]["size"];
        print(file["s3"]["object"])

    return(fileName)