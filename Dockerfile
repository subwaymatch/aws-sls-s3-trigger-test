FROM public.ecr.aws/lambda/python:3.9
COPY requirements.txt ./
RUN pip install -r requirements.txt 
COPY jupyter-cell-scripts/ ./jupyter-cell-scripts/
COPY lambdagrader.py ./
COPY dockerized-grader.py ./
CMD ["dockerized-grader.grade_S3_uploaded_notebook"]