#!/bin/bash

mkdir -p package

pip install -r requirements.txt -t package/

find package -name '*.pyc' -delete
find package -name '__pycache__' -delete
rm -rf package/*.dist-info

cp lambda_function.py package/

cd package
zip -r ../extract_frames_worker_function.zip .
cd ..