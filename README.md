# LambdaGrader Serverless Framework Service

This project is a serverless implementation of the [LambdaGrader](https://github.com/subwaymatch/lambdagrader) project.

## Overview

This project aims to build a Jupyter notebook autograder that runs in a serverless environment. A single lambda invocation grades one Jupyter notebook. Because AWS supports up to 1,000 concurrent executions by default, grading hundreds of submissions can be done simultaneously. The 1,000 concurrent execution limit can also be increased by request.

## Usage

### Deployment

In order to deploy this service, you need to run the following command:

```
$ serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying sls-lambdagrader to stage dev (us-east-1)

✔ Service deployed to stack sls-lambdagrader (300s)

functions:
  hello: my-function1 (1.5 kB)
```

### Invocation

After successful deployment, you can invoke the deployed function by using the following command:

```bash
serverless invoke --function sls_status_check
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function sls_status_check
```

### Docker requirements

LambdaGrader runs dockerized functions to support Python packages that exceed Lambda's file size limit of 50 MB.

Docker is required to build the container while deploying the app. Ensure Docker is running locally.

### Lambda filesystem

The dockerized grading function will write temporary files to the filesystem. Writing to arbitrary paths will fail as Lambda only allows writes to the `/tmp` directory.

### Lambda limits

- Memory allocated to a lambda function cannot exceed 10,240 MB.
- A lambda function cannot run for longer than 15 minutes (900 seconds).
- Lambda includes a 512 MB temporary file system moutned to `/tmp`.
