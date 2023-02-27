import boto3
from botocore.exceptions import ClientError
import json
import os
import pandas as pd
import urllib
import logging
import lambdagrader

def grade_S3_uploaded_notebook(event, context):
    s3_client = boto3.client("s3")

    # retrieve file information
    record = event['Records'][0]
    submission_bucket_name = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    key = urllib.parse.unquote_plus(key, encoding='utf-8')

    graded_bucket_name = os.environ["JUPYTER_NOTEBOOK_GRADED_BUCKET"]

    message = f'file={key} was uploaded to bucket={submission_bucket_name}'
    print(message)

    # any directory other than /tmp is read-only in Lambda
    local_filename = os.path.join('/tmp', 'test.ipynb')
    print(f'local_filename={local_filename}')

    try:
        # s3_client.download_file(bucket_name, 'OBJECT_NAME', 'FILE_NAME')
        s3_client.download_file(submission_bucket_name, key, local_filename)
        print(f'download to {local_filename} successful')
        response = s3_client.upload_file(local_filename, graded_bucket_name, key)
        print(f'upload successful')
    except ClientError as e:
        logging.error(e)

    return {"statusCode": 200, "response": json.dumps(response)}
