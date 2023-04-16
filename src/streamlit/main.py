import streamlit as st
import hashlib
import json
import time
from PIL import Image
import pika
import os

RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmqServer")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", 5672)

PUBLISHING_QUEUE = os.environ.get("PUBLISHING_QUEUE", "prompts")
CONSUMER_QUEUE = os.environ.get("CONSUMER_QUEUE", "generated-images")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials))
channel = connection.channel()
channel.queue_declare(queue=PUBLISHING_QUEUE)
channel.queue_declare(queue=CONSUMER_QUEUE)


def generate_image(prompt: str) -> None:
    # Input image in queue
    prompt_id = request_image(prompt)

    # Wait for image
    image = get_image(prompt_id)
    image = Image.frombytes("RGB", data=image.encode("latin1"), size=(512, 512))
    st.image(image)


def request_image(prompt: str) -> str:
    prompt_id = str(hashlib.sha256(prompt.encode("utf-8")))
    message = {
        "id": prompt_id,
        "prompt": prompt
    }
    channel.basic_publish(exchange='', routing_key=PUBLISHING_QUEUE, body=json.dumps(message))
    return prompt_id

def get_image(prompt_id: str) -> bytes:
    print(prompt_id)
    if prompt_id:
        while True:
            method_frame, header_frame, body = channel.basic_get(CONSUMER_QUEUE)
            body = json.loads(body) if body else None
            if method_frame and body["id"] == prompt_id:
                channel.basic_ack(method_frame.delivery_tag)
                return body["image"]
            time.sleep(0.2)


st.write("# Easy App")
text = st.text_input("Input your text")
if st.button("Generate Image"):
    generate_image(text)








# 






