FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    & pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py ./

CMD ["lambda_function.lambda_handler"]