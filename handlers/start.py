from telebot import types
from database import obtener_creditos

def registrar_start(bot):

    @bot.message_handler(commands=['start'])
    def start(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.row("📱 Recargas")
        markup.row("📺 Megacable")
        markup.row("🌐 Internet")
        markup.row("👨‍💼 Contacto")
        markup.row("💰 Mis Créditos")

        bot.send_message(
            message.chat.id,
            "🏪 Bienvenido\n\nSelecciona una opción:",
            reply_markup=markup
        )

    # -------------------------
    # VER CRÉDITOS
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "💰 Mis Créditos")
    def ver_creditos(message):

        try:
            creditos = obtener_creditos(message.from_user.id)

            bot.send_message(
                message.chat.id,
                f"💰 Tus créditos disponibles: {creditos}\n\n"
                "Cada servicio consume 1 crédito."
            )

        except Exception as e:
            print("ERROR START:", e)
            bot.send_message(message.chat.id, "❌ Error al obtener créditos")
