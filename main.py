import telebot
from config import TOKEN

from handlers.start import registrar_start
from handlers.ventas import registrar_ventas
from handlers.admin import registrar_admin

bot = telebot.TeleBot(TOKEN)

print("🚀 Iniciando bot...")

# -------------------------
# IMPORTANTE: evitar conflictos webhook
# -------------------------
try:
    bot.remove_webhook()
    print("🧹 Webhook eliminado")
except Exception as e:
    print("⚠️ No se pudo eliminar webhook:", e)

# -------------------------
# COMANDO: ID
# -------------------------
@bot.message_handler(commands=['miid'])
def mostrar_mi_id(message):
    bot.send_message(
        message.chat.id,
        f"Tu ID de Telegram es: `{message.from_user.id}`",
        parse_mode="Markdown"
    )

# -------------------------
# COMANDO: TEST
# -------------------------
@bot.message_handler(commands=['test'])
def test_command(message):
    print("🔥 TEST RECIBIDO")
    bot.send_message(message.chat.id, "✅ El bot está funcionando en Railway!")

# -------------------------
# REGISTRAR MODULOS
# -------------------------
print("📦 Cargando módulos...")

registrar_start(bot)
registrar_ventas(bot)
registrar_admin(bot)

print("✅ Módulos cargados correctamente")

# -------------------------
# INICIO POLLING SEGURO
# -------------------------
if __name__ == "__main__":
    print("🤖 Bot iniciado y escuchando mensajes...")

    try:
        bot.infinity_polling(
            skip_pending=True,
            timeout=10,
            long_polling_timeout=10
        )

    except Exception as e:
        print(f"❌ ERROR FATAL: {e}")
