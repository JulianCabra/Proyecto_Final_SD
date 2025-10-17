import pika
import time
import sys

for intento in range(10):
    try:
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'pass'))
        )
        print("[✔] EMOTION conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[!] EMOTION no pudo conectar (intento {intento+1}/10), reintentando...")
        time.sleep(5)
else:
    print("[✖] EMOTION no logró conectarse a RabbitMQ después de varios intentos")
    sys.exit(1)

channel = connection.channel()
channel.queue_declare(queue='emotion_queue')
channel.queue_declare(queue='langchain_queue')

def callback(ch, method, properties, body):
    print(f"[emotion_detector] Texto recibido: {body.decode()}")
    simulated_emotion = "cansado"
    message = f"{body.decode()}|{simulated_emotion}"
    channel.basic_publish(exchange='', routing_key='langchain_queue', body=message)
    print("[emotion_detector] Emoción detectada enviada a langchain_queue")

channel.basic_consume(queue='emotion_queue', on_message_callback=callback, auto_ack=True)
print("[emotion_detector] Esperando mensajes...")
channel.start_consuming()