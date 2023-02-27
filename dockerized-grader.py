import boto3
from botocore.exceptions import ClientError
import json
import os
import pandas as pd
import urllib
import logging
import lambdagrader
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
import shutil
from pathlib import Path
import sys
import platform
import hashlib

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
    submitted_notebook_filename = Path(key).name
    local_notebook_path = os.path.join('/tmp', submitted_notebook_filename)
    print(f'local_notebook_path={local_notebook_path}')

    # s3_client.download_file(bucket_name, 'OBJECT_NAME', 'FILE_NAME')
    s3_client.download_file(submission_bucket_name, key, local_notebook_path)
    print(f'download to {local_notebook_path} successful')
    response = s3_client.upload_file(local_notebook_path, graded_bucket_name, key)
    print(f'upload to {graded_bucket_name} bucket successful')

    print('=============================')
    nb = nbformat.read(local_notebook_path, as_version=4)
    
    test_cases_hash = lambdagrader.get_test_cases_hash(nb)
    
    lambdagrader.preprocess_test_case_cells(nb)
    lambdagrader.add_grader_scripts(nb)
    
    print(f'Grading {local_notebook_path}')
    
    ep = ExecutePreprocessor(
        timeout=600,
        kernel_name='python3',
        allow_errors=True
    )
    ep.preprocess(nb)
    
    # save graded notebook
    converted_notebook_path = local_notebook_path.replace('.ipynb', '-graded.ipynb')
    print(f'converted_notebook_path={converted_notebook_path}')
    with open(converted_notebook_path, mode='w', encoding='utf-8') as f:
        nbformat.write(nb, f)   

    s3_client.upload_file(
        converted_notebook_path,
        graded_bucket_name,
        Path(converted_notebook_path).name
    )
    
    # running the notebook will store the graded result to a JSON file
    # rename graded result JSON file
    graded_result_json_path = local_notebook_path.replace('.ipynb', '-result.json')
    shutil.move('/tmp/lambdagrader-result.json', graded_result_json_path)
    
    # read graded result to generate a summary
    with open(graded_result_json_path, mode='r') as f:
        graded_result = json.load(f)
    
    # add filename
    # we add it here instead of trying to add it within the Jupyter notebook
    # because it is tricky to grab the current file name inside a Jupyter kernel
    graded_result['filename'] = Path(local_notebook_path).name
    
    # MD5 hash of the submitted Jupyter notebook file
    # this can be used to detect duplicate submission to prevent unnecessary re-grading
    with open(local_notebook_path, 'rb') as f:
        graded_result['submission_notebook_hash'] = hashlib.md5(f.read()).hexdigest()
    
    # MD5 hash of test cases code
    # this helps us to identify any potential cases
    # where a learner has modified or deleted the test cases code cell
    graded_result['test_cases_hash'] = test_cases_hash
    
    # store Python version and platform used to run the notebook
    graded_result['grader_python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    graded_result['grader_platform'] = platform.platform()

    # save updated JSON to file
    with open(graded_result_json_path, 'w') as f:
        json.dump(graded_result, f, indent=2)

    s3_client.upload_file(
        graded_result_json_path,
        graded_bucket_name,
        Path(graded_result_json_path).name
    )
        
    # clean up notebook
    lambdagrader.remove_grader_scripts(nb)
    lambdagrader.add_graded_result(nb, graded_result)
        
    # extract user code to a Python file
    extracted_user_code = lambdagrader.extract_user_code_from_notebook(nb)
    extracted_code_path = local_notebook_path.replace('.ipynb', '_user_code.py')
    
    with open(extracted_code_path, "w", encoding="utf-8") as f:
        f.write(extracted_user_code)

    s3_client.upload_file(
        extracted_code_path,
        graded_bucket_name,
        Path(extracted_code_path).name
    )
    
    # store graded result to HTML
    submitted_notebook_filename = Path(local_notebook_path).name
    graded_html_path = local_notebook_path.replace('.ipynb', '-graded.html')
    html_exporter = HTMLExporter()
    r = html_exporter.from_notebook_node(nb, resources={
        'metadata': { 'name': submitted_notebook_filename }
    })
    with open(graded_html_path, 'w', encoding="utf-8") as f:
        f.write(r[0])

    s3_client.upload_file(
        graded_html_path,
        graded_bucket_name,
        Path(graded_html_path).name
    )

    print(f'Complete')

    return {"statusCode": 200, "response": json.dumps(response)}
