import logging
import json
import boto3
import os

def hello(event, context):
    # LambdaContext Object: https://docs.aws.amazon.com/lambda/latest/dg/nodejs-context.html

    bucket = os.environ["JUPYTER_NOTEBOOK_SUBMISSION_BUCKET"]
    region_name = os.environ["REGION_NAME"]

    body = {
        "bucket": bucket,
        "region_name": region_name,
        "message": "Serverless function executed successfully!",
        "input": event,
    }

    print(body)

    return {"statusCode": 200, "body": json.dumps(body)}



# def create_presigned_url(bucket_name, object_name, expiration=3600):
#     """Generate a presigned URL to share an S3 object

#     :param bucket_name: string
#     :param object_name: string
#     :param expiration: Time in seconds for the presigned URL to remain valid
#     :return: Presigned URL as string. If error, returns None.
#     """
#     # Generate a presigned URL for the S3 object
#     s3_client = boto3.client("s3")
#     try:
#         response = s3_client.generate_presigned_url(
#             "get_object",
#             Params={"Bucket": bucket_name, "Key": object_name},
#             ExpiresIn=expiration,
#         )
#     except ClientError as e:
#         logging.error(e)
#         return None
#     # The response contains the presigned URL
#     return response


# def create_presigned_post(
#     bucket_name, object_name, fields=None, conditions=None, expiration=3600
# ):
#     """Generate a presigned URL S3 POST request to upload a file

#     :param bucket_name: string
#     :param object_name: string
#     :param fields: Dictionary of prefilled form fields
#     :param conditions: List of conditions to include in the policy
#     :param expiration: Time in seconds for the presigned URL to remain valid
#     :return: Dictionary with the following keys:
#         url: URL to post to
#         fields: Dictionary of form fields and values to submit with the POST
#     :return: None if error.
#     """

#     # Generate a presigned S3 POST URL
#     s3_client = boto3.client("s3")
#     try:
#         response = s3_client.generate_presigned_post(
#             bucket_name,
#             object_name,
#             Fields=fields,
#             Conditions=conditions,
#             ExpiresIn=expiration,
#         )
#     except ClientError as e:
#         logging.error(e)
#         return None
#     # The response contains the presigned URL and required fields
#     return response


