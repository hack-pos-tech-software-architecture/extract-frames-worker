FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y glib2 libSM libXrender libXext

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    & pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]