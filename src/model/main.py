from diffusers import StableDiffusionPipeline
import torch
import pika
import json
import os

RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmqServer")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", 5672)

CONSUMER_QUEUE = os.environ.get("PUBLISHING_QUEUE", "prompts")
PUBLISHING_QUEUE = os.environ.get("CONSUMER_QUEUE", "generated-images")
MODEL_PATH = "model/openjourney"

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials))
    return connection.channel()


def load_model():
    global model 
    model = StableDiffusionPipeline.from_pretrained(MODEL_PATH, torch_dtype=torch.float32)


def generate_image(ch, method, properties, body):
    body = json.loads(body)
    print("Message received cap")
    prompt = body["prompt"]
    image = model(prompt).images[0]
    message = {
        "id": body["id"],
        "image": image.tobytes().decode("latin1")
    }
    
    # TODO: Connection is lost while image is being generated. Maybe look for timeout options
    ch = get_rabbitmq_connection()
    ch.basic_publish(exchange='', routing_key=PUBLISHING_QUEUE, body=json.dumps(message))



def main():
    load_model()
    channel = get_rabbitmq_connection()
    
    channel.queue_declare(queue=PUBLISHING_QUEUE)
    channel.queue_declare(queue=CONSUMER_QUEUE)

    channel.basic_consume(queue=CONSUMER_QUEUE, on_message_callback=generate_image, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
