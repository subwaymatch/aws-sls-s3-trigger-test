# LambdaGrader Serverless Framework Service

This project is a serverless implementation of [LambdaGrader Local](https://github.com/subwaymatch/lambdagrader) using the [Serverless Framework](https://www.serverless.com/).

## Overview

This project aims to build a Jupyter notebook autograder that runs in a serverless environment. A single lambda invocation grades one Jupyter notebook. Because AWS supports up to 1,000 concurrent executions by default, grading hundreds of submissions can be done simultaneously. The 1,000 concurrent execution limit can also be increased by request.

Another goal of this project is to make it easy for instructors to author a Jupyter notebook for teaching.

### Workflow

![217484470-ab7406ce-bc0b-46a5-bbb2-17bb5fa8a2c7](https://user-images.githubusercontent.com/1064036/221693208-dce4db28-0865-4520-91f1-684c3954f84a.png)

### What about [nbgrader](https://github.com/jupyter/nbgrader)?

[nbgrader](https://github.com/jupyter/nbgrader) is widely used and is a great tool to auto-grade Jupyter notebook assignments. 
I've personally used nbgrader in the past.

However, there are notable limitations to common use cases.

- Creating an nbgrader assignment requires the nbgrader JupyterLab extension.
- Working with multiple graders is challenging unless a shared JupyterHub is used by the instructional team.
- nbgrader uses cell metadata, which cannot be viewed/edited in some Jupyter environments (e.g., [Google Colab](https://colab.research.google.com/)).
- There is a steep learning curve for graders who are not familiar with nbgrader.
- Concurrent grading can crash the server. For example, ~50 students submitting a graded notebook at the same time caused the grading to fail for multiple students.

LambdaGrader uses regular code cells and text cells without an extension to author an autogradable Jupyter notebook.


## Usage

### Deployment

In order to deploy this service, run the following command:

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

List all required packages in `requirements.txt`. `ipython` and `ipykernel` are required to programmatically run a Jupyter notebook using [`ExecutePreprocessor`](https://nbconvert.readthedocs.io/en/latest/api/preprocessors.html).

### Lambda filesystem

The dockerized grading function will write temporary files to the filesystem. Writing to arbitrary paths will fail as Lambda only allows writes to the `/tmp` directory.

### Lambda limits

- Memory allocated to a lambda function cannot exceed 10,240 MB.
- A lambda function cannot run for longer than 15 minutes (900 seconds).
- Lambda includes a 512 MB temporary file system moutned to `/tmp`.

### Checking logs

Lambda function logs can be viewed in AWS CloudWatch.




## Jupyter notebook format

The instructor only authors one "solution" notebook. This notebook contains both the solution code and test cases for all graded parts. Lambdagrader provides a simple drag & drop interface to generate a student-facing notebook which removes the solution codes and obfuscates test cases if required.

### Code cell for learners

Any code between `# YOUR CODE BEGINS` and `# YOUR CODE ENDS` are stripped in the student version.

```python
import pandas as pd

# YOUR CODE BEGINS
sample_series = pd.Series([-20, -10, 10, 20])
# YOUR CODE ENDS

print(sample_series)
```

nbgrader syntax (`### BEGIN SOLUTION`, `### END SOLUTION`) is also supported.

```python
import pandas as pd

### BEGIN SOLUTION
sample_series = pd.Series([-20, -10, 10, 20])
### END SOLUTION

print(sample_series)
```

In the student-distributed notebook, the code cell will look like:

```python
import pandas as pd

# YOUR CODE BEGINS

# YOUR CODE ENDS

print(sample_series)
```

### Graded test cases

A graded test case requires the test case name and number of points.

`_test_case` variable should contain the name of the test case.
`_points` variable should contain the number of points (either in integer or float).

```python
_test_case = 'create-a-pandas-series'
_points = 2

pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
```

### Obfuscate test cases

You may wish to prevent the learners from seeing the test case code. To base64-encode the test cases, you can optionally add `_obfuscate = True`.
Note that this only offers a very basic obfuscation and a student can easily decode the encoded string to find the original code.
We may add an encryption method in the future.

**Instructor notebook**

```python
_test_case = 'create-a-pandas-series'
_points = 2
_obfuscate = True

pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
```

**Student notebook**

```
# DO NOT CHANGE THE CODE IN THIS CELL
_test_case = 'create-a-pandas-series'
_points = 2
_obfuscate = True

import base64 as _b64
_64 = _b64.b64decode('cGQudGVzdGluZy5hc3NlcnRfc2VyaWVzX2VxdWFsKHNhbXBsZV9zZXJpZXMsIHBkLlNlcmllcyhbLT\
IwLCAtMTAsIDEwLCAyMF0pKQ==')
eval(compile(_64, '<string>', 'exec'))
```

### Add hidden test cases

Hidden test cases only run while grading.

**Original test case**

```python
_test_case = 'create-a-pandas-series'
_points = 2

### BEGIN HIDDEN TESTS
pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
### END HIDDEN TESTS
```

**Converted** (before obfuscation)

```python
_test_case = 'create-a-pandas-series'
_points = 2

if 'is_lambdagrader_env' in globals():
    pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
```

## Roadmap

The current goal is to build a working version using the [Serverless framework](https://www.serverless.com/). In the long term, I am looking to...

- Support filesystem (custom input files).
- Build a frontend with drag & drop box for graders.
- Enable encryption for hidden test cases.
- Keep track of submission, results, and output files using a database.
- Detect any modifications to test cases using a hash.
- Migrate `nbconvert.preprocessors.Preprocessor` to [`NotebookClient`](https://nbclient.readthedocs.io/en/latest/client.html). Only minor changes to the API are required
- Add MOSS-like plagiarism detection using [copydetect](https://github.com/blingenf/copydetect).
