from database import agregar_creditos, obtener_creditos

ADMIN_ID = 8954020327  # Tu ID

def registrar_admin(bot):
    @bot.message_handler(commands=['addcredits'])
    def add_credits(message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "❌ No tienes permisos")
            return
        try:
            parts = message.text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Uso: /addcredits <user_id> <cantidad>")
                return
            user_id = int(parts[1])
            cantidad = int(parts[2])
            agregar_creditos(user_id, cantidad)
            nuevos = obtener_creditos(user_id)
            bot.send_message(message.chat.id, f"✅ Agregados {cantidad} créditos. Saldo: {nuevos}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")