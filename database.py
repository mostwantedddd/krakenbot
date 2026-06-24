import os
import sys
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: Variable DATABASE_URL no encontrada en Railway.", file=sys.stderr)
    sys.exit(1)

try:
    # auto commit = True hace que los cambios se guarden solos, sin errores
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    conn.autocommit = True
    print("✅ [LOG] Conectado exitosamente a PostgreSQL.", file=sys.stderr)
except Exception as e:
    print(f"❌ [LOG] Error conectando a PostgreSQL: {e}", file=sys.stderr)
    conn = None
    cursor = None

cursor = conn.cursor()

# Crear la tabla (PostgreSQL usa ON CONFLICT, no INSERT OR IGNORE)
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

def descontar_creditos(user_id, cantidad):
    cursor.execute(
        "UPDATE usuarios SET creditos = creditos - %s WHERE user_id = %s AND creditos >= %s",
        (cantidad, user_id, cantidad)
    )
    conn.commit()
