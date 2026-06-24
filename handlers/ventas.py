import re
from database import obtener_creditos, descontar_credito, agregar_creditos  # Importar funciones

def registrar_ventas(bot):

    estados = {}

    @bot.message_handler(func=lambda m: m.text == "📱 Recargas")
    def recargas(message):
        # Verificar créditos antes de iniciar
        creditos = obtener_creditos(message.from_user.id)
        
        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                "❌ No tienes créditos suficientes.\n\n"
                f"💰 Créditos actuales: {creditos}\n\n"
                "Contacta al administrador para comprar más."
            )
            return
        
        estados[message.chat.id] = "recarga"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía el número a recargar (10 dígitos)"
        )

    @bot.message_handler(func=lambda m: m.text == "📺 Megacable")
    def megacable(message):
        # Verificar créditos antes de iniciar
        creditos = obtener_creditos(message.from_user.id)
        
        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                "❌ No tienes créditos suficientes.\n\n"
                f"💰 Créditos actuales: {creditos}\n\n"
                "Contacta al administrador para comprar más."
            )
            return

        estados[message.chat.id] = "megacable"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía tu número de contrato"
        )

    @bot.message_handler(func=lambda m: m.text == "🌐 Internet")
    def internet(message):
        # Verificar créditos antes de iniciar
        creditos = obtener_creditos(message.from_user.id)
        
        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                "❌ No tienes créditos suficientes.\n\n"
                f"💰 Créditos actuales: {creditos}\n\n"
                "Contacta al administrador para comprar más."
            )
            return

        estados[message.chat.id] = "internet"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía tu número de servicio"
        )

    @bot.message_handler(func=lambda m: True)
    def capturar(message):

        estado = estados.get(message.chat.id)

        if estado == "recarga":

            numero = re.sub(r"\D", "", message.text)

            if len(numero) == 10:
                bot.send_message(
                    message.chat.id,
                    f"✅ Número detectado: {numero}\n\nAhora envía el monto."
                )

                estados[message.chat.id] = "monto_recarga"

            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Debe tener 10 dígitos."
                )

        elif estado == "megacable":

            contrato = re.sub(r"\D", "", message.text)

            if len(contrato) >= 6:
                # Descontar crédito al completar
                descontar_credito(message.from_user.id)
                creditos_restantes = obtener_creditos(message.from_user.id)
                
                bot.send_message(
                    message.chat.id,
                    f"✅ Contrato Megacable detectado:\n{contrato}\n\n"
                    f"💳 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Número de contrato inválido."
                )

        elif estado == "internet":

            servicio = re.sub(r"\D", "", message.text)

            if len(servicio) >= 6:
                # Descontar crédito al completar
                descontar_credito(message.from_user.id)
                creditos_restantes = obtener_creditos(message.from_user.id)
                
                bot.send_message(
                    message.chat.id,
                    f"✅ Servicio detectado:\n{servicio}\n\n"
                    f"💳 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Número inválido."
                )
        
        elif estado == "monto_recarga":
            # Validar monto y completar recarga
            try:
                monto = float(message.text)
                if monto > 0:
                    # Descontar crédito al completar
                    descontar_credito(message.from_user.id)
                    creditos_restantes = obtener_creditos(message.from_user.id)
                    
                    bot.send_message(
                        message.chat.id,
                        f"✅ Recarga procesada:\n"
                        f"Monto: ${monto:.2f}\n\n"
                        f"💳 Créditos restantes: {creditos_restantes}"
                    )
                    estados.pop(message.chat.id)
                else:
                    bot.send_message(
                        message.chat.id,
                        "❌ Monto inválido. Envía un número positivo."
                    )
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ Envía un monto válido (ejemplo: 100)"
                )