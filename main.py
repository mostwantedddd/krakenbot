import telebot
from config import TOKEN
from handlers.start import registrar_start
from handlers.ventas import registrar_ventas
from handlers.admin import registrar_admin

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

# ESTE COMANDO TE DIRÁ TU ID REAL EN TELEGRAM
@bot.message_handler(commands=['miid'])
def mostrar_mi_id(message):
    bot.send_message(message.chat.id, f"Tu ID de Telegram es: `{message.from_user.id}`", parse_mode="Markdown")

# COMANDO DE PRUEBA PARA SABER SI EL BOT ESTÁ VIVO
@bot.message_handler(commands=['test'])
def test_command(message):
    bot.send_message(message.chat.id, "✅ ¡El bot está funcionando en Railway!")

print("🚀 Iniciando módulos del bot...")
registrar_start(bot)
registrar_ventas(bot)
registrar_admin(bot)

print("Bot iniciado...")
try:
    # Non_stop=True evita que el bot se caiga por errores de red pequeños
    bot.polling(non_stop=True, skip_pending=True)
except Exception as e:
    print(f"❌ ERROR FATAL: El bot se ha caído por: {e}")
