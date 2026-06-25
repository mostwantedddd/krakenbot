from telebot import types
from database import obtener_creditos

# Diccionario para guardar el monto pendiente de cada usuario mientras envía el comprobante
user_deposit_state = {}

# ⚠️ CAMBIA ESTO POR TU ID DE TELEGRAM (El ID del administrador)
ADMIN_CHAT_ID = 8954020327, 8010899471

def registrar_start(bot):
    # Datos bancarios
    CLABE = "646180401609592944"
    BANCO = "OpenBank"
    TITULAR = "Josue Daniel Torres Cortes"
    CONVERSION = "1 Peso 1 Crédito"

    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📱 Recargas", "📺 Megacable")
        markup.row("🌐 Internet", "👨‍💼 Contacto")
        markup.row("💰 Mis Créditos", "💳 Depositar")

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
                f"💰 Tus créditos disponibles: {creditos}\n"
            )
        except Exception as e:
            print("ERROR START:", e)
            bot.send_message(message.chat.id, "❌ Error al obtener créditos")

    # -------------------------
    # OPCIÓN DEPOSITAR (Submenú)
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "💳 Depositar")
    def menu_deposito(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("💵 Depositar $100", "💵 Depositar $150")
        markup.row("💵 Depositar $200", "💵 Depositar $500")
        markup.row("💵 Depositar $1000")
        markup.row("🔙 Volver")

        bot.send_message(
            message.chat.id,
            "🏦 Selecciona cuánto deseas depositar:",
            reply_markup=markup
        )

    # -------------------------
    # SELECCIÓN DE MONTO (GUARDAMOS EL MONTO)
    # -------------------------
    @bot.message_handler(func=lambda m: m.text and "Depositar $" in m.text)
    def seleccionar_monto(message):
        monto = message.text.replace("💵 Depositar $", "").strip()
        
        # Guardamos el monto en la memoria del bot asociado al ID del usuario
        user_deposit_state[message.chat.id] = monto

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📨 Enviar comprobante")
        markup.row("🔙 Volver")

        texto = (
            f"✅ Monto seleccionado: ${monto}\n\n"
            f"💳 Deposita a la siguiente CLABE:\n{CLABE}\n\n"
            f"Banco: {BANCO}\n"
            f"A nombre de: {TITULAR}\n\n"
            f"CONVERSION {CONVERSION}\n\n"
            "Cuando termines, presiona el botón para enviar tu comprobante."
        )

        bot.send_message(
            message.chat.id,
            texto,
            reply_markup=markup
        )

    # -------------------------
    # ENVIAR COMPROBANTE (Pide la foto)
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "📨 Enviar comprobante")
    def esperar_comprobante(message):
        bot.send_message(
            message.chat.id,
            "📷 Por favor, envía una foto o captura de tu comprobante de pago.",
            reply_markup=types.ReplyKeyboardRemove() # Limpia el teclado
        )

    # -------------------------
    # RECEPCIÓN DE FOTO (ENVÍA AL ADMIN)
    # -------------------------
    @bot.message_handler(content_types=['photo'])
    def recepcion_comprobante(message):
        user_id = message.chat.id
        
        # Recuperamos el monto que el usuario había seleccionado
        monto = user_deposit_state.get(user_id, "No especificado")
        
        # Obtenemos la mejor calidad de la foto
        file_id = message.photo[-1].file_id
        user = message.from_user
        username = f"@{user.username}" if user.username else "Sin username"
        
        # Construimos el mensaje para el administrador
        caption = (
            f"📥 **NUEVO DEPÓSITO RECIBIDO**\n\n"
            f"📌 Usuario: {user.first_name} {user.last_name or ''}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🔗 Username: {username}\n"
            f"💰 Monto a depositar: ${monto}\n\n"
            "⬇️ Comprobante adjunto abajo."
        )

        try:
            # Enviamos la foto y los datos al administrador
            bot.send_photo(ADMIN_CHAT_ID, file_id, caption=caption, parse_mode='Markdown')
            
            # Confirmamos al usuario que se envió correctamente
            bot.send_message(
                user_id, 
                "✅ Comprobante enviado con éxito al administrador.\n\nEn breve revisaremos tu pago y te acreditaremos los créditos.",
                reply_markup=types.ReplyKeyboardRemove() # Limpia teclado
            )
            
            # Eliminamos el monto guardado de la memoria porque el proceso terminó
            if user_id in user_deposit_state:
                del user_deposit_state[user_id]

            # Regresamos al menú principal automáticamente
            start(message)

        except Exception as e:
            print(f"ERROR AL ENVIAR AL ADMIN: {e}")
            bot.send_message(
                user_id, 
                "❌ Hubo un error interno al enviar tu comprobante. Por favor, contacta directamente al administrador.",
                reply_markup=types.ReplyKeyboardRemove()
            )

    # -------------------------
    # VOLVER AL MENÚ PRINCIPAL
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "🔙 Volver")
    def volver_menu(message):
        # Si vuelve atrás, borramos el monto que tenía guardado en memoria
        if message.chat.id in user_deposit_state:
            del user_deposit_state[message.chat.id]
        start(message)
