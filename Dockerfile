FROM public.ecr.aws/lambda/python:3.9
COPY requirements.txt ./
RUN pip install -r requirements.txt 
COPY jupyter-cell-scripts ./
COPY lambdagrader.py ./
COPY app.py ./
CMD ["app.grade_S3_uploaded_notebook"]