import pika
import time
import sys

for intento in range(10):
    try:
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'pass'))
        )
        print("[✔] TEXT_TO_SPEECH conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[!] TEXT_TO_SPEECH no pudo conectar (intento {intento+1}/10), reintentando...")
        time.sleep(5)
else:
    print("[✖] TEXT_TO_SPEECH no logró conectarse a RabbitMQ después de varios intentos")
    sys.exit(1)


channel = connection.channel()
channel.queue_declare(queue='tts_queue')

def callback(ch, method, properties, body):
    print(f"[text_to_speech] Mensaje final para usuario: {body.decode()}")

channel.basic_consume(queue='tts_queue', on_message_callback=callback, auto_ack=True)
print("[text_to_speech] Esperando mensajes...")
channel.start_consuming()
