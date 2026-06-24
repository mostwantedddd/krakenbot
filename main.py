import telebot
from config import TOKEN
from handlers.start import registrar_start
from handlers.ventas import registrar_ventas
from handlers.admins import registrar_admin

bot = telebot.TeleBot(TOKEN)

print("🚀 Iniciando módulos del bot...")
registrar_start(bot)
registrar_ventas(bot)
registrar_admin(bot)

print("Bot iniciado...")
bot.infinity_polling(skip_pending=True)
