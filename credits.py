import json
import os

FILE = "credits.json"

# -------------------------
# CARGAR DATOS
# -------------------------
def load_data():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)

# -------------------------
# GUARDAR DATOS
# -------------------------
def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------
# OBTENER CREDITOS
# -------------------------
def obtener_creditos(user_id):
    data = load_data()
    return data.get(str(user_id), 0)

# -------------------------
# AGREGAR CREDITOS
# -------------------------
def agregar_creditos(user_id, amount):
    data = load_data()

    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = 0

    data[user_id] += amount

    save_data(data)

# -------------------------
# DESCONTAR CREDITOS
# -------------------------
def descontar_credito(user_id, amount=1):
    data = load_data()

    user_id = str(user_id)

    if data.get(user_id, 0) >= amount:
        data[user_id] -= amount
        save_data(data)
        return True

    return False
