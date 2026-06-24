print("🔥 comando cargado")
from database import agregar_creditos

ADMIN_ID = 8954020327

def registrar_admin(bot):

    @bot.message_handler(commands=['addcredits'])
    def add_credits(message):
        print("🔥 comando recibido")

        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "❌ No tienes permisos.")
            return

        try:
            parts = message.text.split()

            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Uso: /addcredits <id> <cantidad>")
                return

            user_id = int(parts[1])
            amount = int(parts[2])

            agregar_creditos(user_id, amount)

            bot.send_message(
                message.chat.id,
                f"✅ Se agregaron {amount} créditos a {user_id}"
            )

        except Exception as e:
            print("ERROR:", e)
            bot.send_message(message.chat.id, "❌ Error interno")
