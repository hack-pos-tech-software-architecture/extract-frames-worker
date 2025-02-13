import boto3
import json
import os
import uuid
import cv2
import tempfile

# Configuração do S3
s3_client = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "upload-videos-1"

# Configuração do SQS
# sqs_client = boto3.client("sqs")
# SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/seu-id/seu-queue-compressao"


def extract_frames(video_path, output_folder):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    frames = []

    while success:
        frame_filename = f"frame-{count}.jpg"
        frame_path = os.path.join(output_folder, frame_filename)
        cv2.imwrite(frame_path, image)
        frames.append(frame_filename)
        success, image = vidcap.read()
        count += 1

    return frames


def lambda_handler(event, context):
    for record in event["Records"]:
        message = json.loads(record["body"])
        file_key = message["file_key"]

        temp_dir = tempfile.mkdtemp()
        local_video_path = os.path.join(temp_dir, "video.mp4")

        try:
            # Baixa o vídeo do S3
            s3_client.download_file(BUCKET_NAME, file_key, local_video_path)

            # Extrai frames do vídeo
            frames = extract_frames(local_video_path, temp_dir)

            # Faz upload dos frames para o S3
            for frame in frames:
                frame_path = os.path.join(temp_dir, frame)
                frame_key = f"frames/{uuid.uuid4()}-{frame}"
                s3_client.upload_file(frame_path, BUCKET_NAME, frame_key)

            # Envia mensagem para próxima etapa
            # message_body = json.dumps({"frames": frames, "bucket": BUCKET_NAME})
            # sqs_client.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=message_body)

        except Exception as e:
            print(f"Erro no processamento do vídeo: {str(e)}")
            raise e

    return {"status": "Processamento concluído"}
