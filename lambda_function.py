import json

def lambda_handler(event, context):
    # Processa cada mensagem recebida
    for record in event['Records']:
        # Converte o corpo da mensagem para um objeto Python
        message_body = json.loads(record['body'])
        
        # Exibe o conteúdo da mensagem
        print("Mensagem recebida:", message_body)
        
        # Aqui você pode adicionar a lógica para processar a mensagem
        # Por exemplo, salvar em um banco de dados, enviar um email, etc.
    
    return {
        'statusCode': 200,
        'body': json.dumps('Mensagem processada com sucesso!')
    }