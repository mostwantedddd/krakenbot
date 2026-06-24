import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
  print("✅ [LOG] Conectado exitosamente a PostgreSQL.", file=sys.stderr)
    except Exception as e:
        print(f"❌ [LOG] ERROR GRAVE conectando a PostgreSQL: {e}", file=sys.stderr)
        # Forzamos el cierre para que veas el error en rojo en los logs
        sys.exit(1)
else:
    # Si no encuentra DATABASE_URL, usa SQLite (Esto es el enemigo de los créditos)
    print("⚠️ [LOG] ATENCIÓN: Usando SQLite EFÍMERO (local). Los créditos se borrarán al reiniciar Railway.", file=sys.stderr)
    conn = sqlite3.connect("bot.db", check_same_thread=False)

if not DATABASE_URL:
    raise Exception("DATABASE_URL no encontrada")

conn = psycopg2.connect(
    DATABASE_URL,
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
