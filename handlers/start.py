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

    @bot.message_handler(func=lambda m: m.text == "💰 Mis Créditos")
    def ver_creditos(message):

        creditos = obtener_creditos(message.from_user.id)

        bot.send_message(
            message.chat.id,
            f"💰 Tus créditos disponibles: {creditos}\n\n"
            "Cada servicio consume 1 crédito."
        )
