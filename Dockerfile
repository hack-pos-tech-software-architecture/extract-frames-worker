FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y libglib2.0 libsm6 libxrender1 libxext6

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]