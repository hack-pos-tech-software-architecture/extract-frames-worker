import cv2
import numpy as np

def lambda_handler(event, context):
    # Cria uma imagem preta
    img = np.zeros((500, 500, 3), np.uint8)

    # Desenha um círculo
    cv2.circle(img, (250, 250), 100, (0, 255, 0), -1)

    # Salva a imagem (apenas para teste)
    cv2.imwrite('/tmp/output.png', img)

    return {
        'statusCode': 200,
        'body': 'OpenCV funcionando na Lambda!'
    }