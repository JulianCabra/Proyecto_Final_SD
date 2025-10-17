import pika
import time
import sys

for intento in range(10):
    try:
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'pass'))
        )
        print("[✔] SPEECH_TO_TEXT conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[!] SPEECH_TO_TEXT no pudo conectar (intento {intento+1}/10), reintentando...")
        time.sleep(5)
else:
    print("[✖] SPEECH_TO_TEXT no logró conectarse a RabbitMQ después de varios intentos")
    sys.exit(1)


channel = connection.channel()
channel.queue_declare(queue='voice_input')
channel.queue_declare(queue='emotion_queue')

def callback(ch, method, properties, body):
    print(f"[speech_to_text] Recibido: {body.decode()}")
    simulated_text = "Estoy cansado pero satisfecho con la clase"
    channel.basic_publish(exchange='', routing_key='emotion_queue', body=simulated_text)
    print("[speech_to_text] Texto transcrito enviado a emotion_queue")

channel.basic_consume(queue='voice_input', on_message_callback=callback, auto_ack=True)
print("[speech_to_text] Esperando mensajes...")
channel.start_consuming()

