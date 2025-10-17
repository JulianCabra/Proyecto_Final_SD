import pika, psycopg2, os, time, sys

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "afterclass_db")
DB_USER = os.getenv("DB_USER", "afterclass_user")
DB_PASS = os.getenv("DB_PASS", "afterclass_pass")

time.sleep(5)

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
)
cursor = conn.cursor()

# Conexión a RabbitMQ con reintentos
for intento in range(10):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials('user', 'pass')
            )
        )
        print("[✔] DB conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[!] DB no pudo conectar (intento {intento+1}/10), reintentando...")
        time.sleep(5)
else:
    print("[✖] DB no logró conectarse a RabbitMQ después de varios intentos")
    sys.exit(1)

channel = connection.channel()
channel.queue_declare(queue='db_queue')

def callback(ch, method, properties, body):
    print(f"[database_service] Recibido: {body.decode()}")
    try:
        user_id, text, emotion, response = body.decode().split('|')

        cursor.execute(
            "INSERT INTO chats (user_id, input_text, detected_emotion, response_text) VALUES (%s, %s, %s, %s)",
            (user_id, text, emotion, response)
        )
        conn.commit()
        print(f"[database_service] Chat guardado para user_id {user_id}.")
    except Exception as e:
        conn.rollback()
        print(f"[database_service] Error al guardar: {e}")

channel.basic_consume(queue='db_queue', on_message_callback=callback, auto_ack=True)
print("[database_service] Esperando mensajes...")
channel.start_consuming()
