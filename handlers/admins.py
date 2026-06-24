ADMIN_ID = 8954020327

def registrar_start(bot)

@bot.message_handler(commands=['add'])
def add_credits(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, amount = message.text.split()
        agregar_creditos(int(user_id), int(amount))

        bot.send_message(message.chat.id, "✔ Créditos agregados")
    except:
        bot.send_message(message.chat.id, "Uso: /add user_id cantidad")
