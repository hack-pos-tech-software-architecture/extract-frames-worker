import requests


def lambda_handler(event, context):
    response = requests.get("https://www.google.com.br/")
    return {
        'statusCode': 200,
        'body': f'Hello from Lambda! Request Status: {response.status_code}'
    }