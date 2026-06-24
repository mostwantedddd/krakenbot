import os
import sys
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

# Si no encuentra la variable, el bot se detiene y te muestra el error en los Logs
if not DATABASE_URL:
    print("❌ ERROR GRAVE: No se encontró la variable DATABASE_URL en Railway.", file=sys.stderr)
    sys.exit(1)

try:
    # Conexión directa a PostgreSQL (no necesitas ni sqlite, ni urlparse)
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    print("✅ [LOG] Conectado exitosamente a PostgreSQL.", file=sys.stderr)
except Exception as e:
    print(f"❌ [LOG] ERROR GRAVE conectando a PostgreSQL: {e}", file=sys.stderr)
    sys.exit(1)

cursor = conn.cursor()

# Crear la tabla usando los mismos nombres de tu versión anterior
cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (user_id BIGINT PRIMARY KEY, creditos INTEGER DEFAULT 0)")
conn.commit()

def obtener_creditos(user_id):
    cursor.execute("SELECT creditos FROM usuarios WHERE user_id = %s", (user_id,))
    fila = cursor.fetchone()
    if fila:
        return fila[0]
    cursor.execute("INSERT INTO usuarios (user_id, creditos) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    conn.commit()
    return 0

def agregar_creditos(user_id, cantidad):
    cursor.execute("INSERT INTO usuarios (user_id, creditos) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    cursor.execute("UPDATE usuarios SET creditos = creditos + %s WHERE user_id = %s", (cantidad, user_id))
    conn.commit()

def descontar_credito(user_id):
    cursor.execute("UPDATE usuarios SET creditos = creditos - 1 WHERE user_id = %s AND creditos > 0", (user_id,))
    conn.commit()
