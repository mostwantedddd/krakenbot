import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Modo Railway (PostgreSQL)
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
else:
    # Modo local (SQLite)
    conn = sqlite3.connect("bot.db", check_same_thread=False)

cursor = conn.cursor()

# Crear tabla en la base de datos que usemos
cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (user_id BIGINT PRIMARY KEY, creditos INTEGER DEFAULT 0)")
conn.commit()

def obtener_creditos(user_id):
    if DATABASE_URL:
        cursor.execute("SELECT creditos FROM usuarios WHERE user_id = %s", (user_id,))
    else:
        cursor.execute("SELECT creditos FROM usuarios WHERE user_id = ?", (user_id,))
        
    fila = cursor.fetchone()
    if fila:
        return fila[0]
    
    # Crear usuario si no existe
    if DATABASE_URL:
        cursor.execute("INSERT INTO usuarios (user_id, creditos) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    else:
        cursor.execute("INSERT OR IGNORE INTO usuarios (user_id, creditos) VALUES (?, 0)", (user_id,))
        
    conn.commit()
    return 0

def agregar_creditos(user_id, cantidad):
    # Insertar o ignorar si ya existe
    if DATABASE_URL:
        cursor.execute("INSERT INTO usuarios (user_id, creditos) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING", (user_id,))
        cursor.execute("UPDATE usuarios SET creditos = creditos + %s WHERE user_id = %s", (cantidad, user_id))
    else:
        cursor.execute("INSERT OR IGNORE INTO usuarios (user_id, creditos) VALUES (?, 0)", (user_id,))
        cursor.execute("UPDATE usuarios SET creditos = creditos + ? WHERE user_id = ?", (cantidad, user_id))
        
    conn.commit()

def descontar_credito(user_id):
    if DATABASE_URL:
        cursor.execute("UPDATE usuarios SET creditos = creditos - 1 WHERE user_id = %s", (user_id,))
    else:
        cursor.execute("UPDATE usuarios SET creditos = creditos - 1 WHERE user_id = ?", (user_id,))
        
    conn.commit()
