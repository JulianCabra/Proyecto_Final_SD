from flask import Flask, request, jsonify
import psycopg2, hashlib, jwt, datetime, os

# Configuración
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "afterclass_db")
DB_USER = os.getenv("DB_USER", "afterclass_user")
DB_PASS = os.getenv("DB_PASS", "afterclass_pass")
SECRET_KEY = "afterclass_secret"

app = Flask(__name__)

conn = psycopg2.connect(
    host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
)
cursor = conn.cursor()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Faltan campos"}), 400

    hash_pass = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hash_pass)
        )
        conn.commit()
        return jsonify({"message": "Usuario registrado"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if hashlib.sha256(password.encode()).hexdigest() != user[1]:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    token = jwt.encode({
        "user_id": user[0],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token}), 200

@app.route("/chats", methods=["GET"])
def get_chats():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
    except Exception:
        return jsonify({"error": "Token inválido o expirado"}), 401

    cursor.execute("SELECT input_text, detected_emotion, response_text, created_at FROM chats WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()

    chats = [{
        "input_text": r[0],
        "emotion": r[1],
        "response": r[2],
        "timestamp": r[3].isoformat()
    } for r in rows]

    return jsonify(chats), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
