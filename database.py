import os
import psycopg2

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

# 🔹 Crear usuario si no existe
def crear_usuario(user_id):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_id, credits)
        VALUES (%s, 0)
        ON CONFLICT (user_id) DO NOTHING;
    """, (user_id,))
    conn.commit()
    cur.close()

# 🔹 Obtener créditos
def obtener_creditos(user_id):
    crear_usuario(user_id)

    cur = conn.cursor()
    cur.execute("SELECT credits FROM users WHERE user_id = %s", (user_id,))
    data = cur.fetchone()
    cur.close()

    return data[0] if data else 0

# 🔹 Agregar créditos (RECARGA)
def agregar_creditos(user_id, amount):
    crear_usuario(user_id)

    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET credits = credits + %s
        WHERE user_id = %s;
    """, (amount, user_id))
    conn.commit()
    cur.close()

# 🔹 Descontar crédito (USO)
def descontar_credito(user_id, amount=1):
    crear_usuario(user_id)

    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET credits = credits - %s
        WHERE user_id = %s AND credits >= %s;
    """, (amount, user_id, amount))
    conn.commit()
    cur.close()
