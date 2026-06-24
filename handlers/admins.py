print("✅ admin cargado")
from database import agregar_creditos

ADMIN_ID = 8954020327  # Tu ID

def registrar_admin(bot):
    # Vuelvo a poner 'addcredits' para que no tengas que aprender otro comando
    @bot.message_handler(commands=['addcredits'])
    def add_credits(message):
        
        # Registro en los Logs de Railway por si falla
        print(f"🔹 [LOG] Admin intentó usar comando: {message.text}")

        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "❌ No tienes permisos.")
            return

        try:
            parts = message.text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Uso correcto: /addcredits <user_id> <cantidad>")
                return

            # Extraer datos
            user_id = int(parts[1])
            amount = int(parts[2])

            # Ejecutar en la base de datos
            agregar_creditos(user_id, amount)

            bot.send_message(
                message.chat.id,
                f"✅ Se agregaron {amount} créditos al usuario {user_id}"
            )

        except ValueError:
            bot.send_message(message.chat.id, "❌ Error: El ID y la cantidad deben ser números.")
        except Exception as e:
            print(f"❌ ERROR EN EL COMANDO: {e}")
            bot.send_message(message.chat.id, "❌ Ocurrió un error interno. Revisa los Logs de Railway.")
