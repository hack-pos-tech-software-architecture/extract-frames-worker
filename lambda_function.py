import boto3
import json
import os
import uuid
import cv2
import tempfile
import queue
import concurrent.futures
import threading
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do S3
s3_client = boto3.client("s3", region_name="us-east-1")
BUCKET_VIDEO_PROCESSOR_S3 = os.environ.get("BUCKET_VIDEO_PROCESSOR_S3")

# Configuração do SQS
sqs_client = boto3.client("sqs", region_name="us-east-1")
SQS_QUEUE_ZIP_IMAGES_URL = os.environ.get("SQS_QUEUE_ZIP_IMAGES_URL")


def save_frame(image, frame_path):
    cv2.imwrite(frame_path, image)


def upload_frames(frames, temp_dir, bucket_name):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for frame in frames:
            frame_path = os.path.join(temp_dir, frame)
            frame_key = f"frames/{uuid.uuid4()}-{frame}"
            futures.append(
                executor.submit(
                    s3_client.upload_file, frame_path, bucket_name, frame_key
                )
            )

        concurrent.futures.wait(futures)


def read_frames(video_path, frame_queue):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_queue.put((count, image))
        success, image = vidcap.read()
        count += 1

    frame_queue.put(None)


def extract_frames(video_path, output_folder):
    frame_queue = queue.Queue(maxsize=10)  # Buffer de frames
    reader_thread = threading.Thread(target=read_frames, args=(video_path, frame_queue))
    reader_thread.start()

    frames = []

    with concurrent.futures.ThreadPoolExecutor() as executor:  # Usando ThreadPoolExecutor
        futures = {}

        while True:
            data = frame_queue.get()
            if data is None:
                break  # Fim da leitura

            count, image = data
            frame_filename = f"frame-{count}.jpg"
            frame_path = os.path.join(output_folder, frame_filename)
            frames.append(frame_filename)

            # Processa o salvamento dos frames em paralelo
            future = executor.submit(save_frame, image, frame_path)
            futures[future] = frame_filename

        # Aguarda todas as tasks terminarem
        concurrent.futures.wait(futures)

    reader_thread.join()  # Aguarda a thread de leitura finalizar
    return frames


def lambda_handler(event, context):

    for record in event["Records"]:
        message = json.loads(record["body"])
        file_key = message["file_key"]

        # Verifica se o objeto existe no S3
        try:
            s3_client.head_object(Bucket=BUCKET_VIDEO_PROCESSOR_S3, Key=file_key)
            print("Objeto encontrado no S3.")
        except Exception as e:
            print(f"Erro ao verificar objeto no S3: {str(e)}")
            raise e

        temp_dir = tempfile.mkdtemp()
        local_video_path = os.path.join(temp_dir, "video.mp4")

        try:
            s3_client.download_file(
                BUCKET_VIDEO_PROCESSOR_S3, file_key, local_video_path
            )
            print("Download do vídeo concluído.")

            frames = extract_frames(local_video_path, temp_dir)
            print(f"Extraídos {len(frames)} frames.")

            upload_frames(frames, temp_dir, BUCKET_VIDEO_PROCESSOR_S3)
            print("Upload dos frames concluído.")

            # Envia mensagem para próxima etapa
            message_body = json.dumps(
                {"frames": frames, "bucket": BUCKET_VIDEO_PROCESSOR_S3}
            )
            sqs_client.send_message(
                QueueUrl=SQS_QUEUE_ZIP_IMAGES_URL,
                MessageBody=message_body, 
                MeMessageGroupId="zipImages",
                MessageDeduplicationId=str(uuid.uuid4())
            )

        except Exception as e:
            print(f"Erro no processamento do vídeo: {str(e)}")
            raise e

    return {"statusCode": 200, "message": "Processamento concluído"}
