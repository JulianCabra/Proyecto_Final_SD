import pika
import time
import sys

for intento in range(10):
    try:
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'pass'))
        )
        print("[✔] LANGCHAIN conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[!] LANGCHAIN no pudo conectar (intento {intento+1}/10), reintentando...")
        time.sleep(5)
else:
    print("[✖] LANGCHAIN no logró conectarse a RabbitMQ después de varios intentos")
    sys.exit(1)

channel = connection.channel()
channel.queue_declare(queue='langchain_queue')
channel.queue_declare(queue='tts_queue')
channel.queue_declare(queue='db_queue')

def callback(ch, method, properties, body):
    text, emotion = body.decode().split('|')
    simulated_response = "Te recomiendo tomar un descanso corto y escuchar algo relajante."
    print(f"[langchain_brain] Generada respuesta: {simulated_response}")
    channel.basic_publish(exchange='', routing_key='tts_queue', body=simulated_response)
    db_data = f"{text}|{emotion}|{simulated_response}"
    channel.basic_publish(exchange='', routing_key='db_queue', body=db_data)

channel.basic_consume(queue='langchain_queue', on_message_callback=callback, auto_ack=True)
print("[langchain_brain] Esperando mensajes...")
channel.start_consuming()
