import re
from database import obtener_creditos, descontar_creditos

def registrar_ventas(bot):

    estados = {}

    # -------------------------
    # RECARGAS
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "📱 Recargas")
    def recargas(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                f"❌ No tienes créditos suficientes.\n\n💰 Créditos actuales: {creditos}"
            )
            return

        estados[message.chat.id] = "recarga"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía el número a recargar (10 dígitos)"
        )

    # -------------------------
    # MEGACABLE
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "📺 Megacable")
    def megacable(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                f"❌ No tienes créditos suficientes.\n\n💰 Créditos actuales: {creditos}"
            )
            return

        estados[message.chat.id] = "megacable"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía tu número de contrato"
        )

    # -------------------------
    # INTERNET
    # -------------------------
    @bot.message_handler(func=lambda m: m.text == "🌐 Internet")
    def internet(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(
                message.chat.id,
                f"❌ No tienes créditos suficientes.\n\n💰 Créditos actuales: {creditos}"
            )
            return

        estados[message.chat.id] = "internet"

        bot.send_message(
            message.chat.id,
            f"💳 Créditos disponibles: {creditos}\n\n"
            "Envía tu número de servicio"
        )

    # -------------------------
    # CAPTURA DE MENSAJES (FIX IMPORTANTE)
    # -------------------------
    @bot.message_handler(func=lambda m: m.chat.id in estados)
    def capturar(message):

        estado = estados.get(message.chat.id)

        # -------------------------
        # RECARGA FLUJO
        # -------------------------
        if estado == "recarga":

            numero = re.sub(r"\D", "", message.text)

            if len(numero) == 10:

                estados[message.chat.id] = "monto_recarga"

                bot.send_message(
                    message.chat.id,
                    f"✅ Número detectado: {numero}\n\nAhora envía el monto."
                )
            else:
                bot.send_message(message.chat.id, "❌ Debe tener 10 dígitos.")

        # -------------------------
        # MONTO RECARGA
        # -------------------------
        elif estado == "monto_recarga":

            try:
                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(message.chat.id, "❌ Monto inválido")
                    return

                descontar_credito(message.from_user.id)
                creditos_restantes = obtener_creditos(message.from_user.id)

                bot.send_message(
                    message.chat.id,
                    f"✅ Recarga procesada\n"
                    f"Monto: ${monto:.2f}\n\n"
                    f"💳 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(message.chat.id, "❌ Envía un monto válido")

        # -------------------------
        # MEGACABLE
        # -------------------------
        elif estado == "megacable":

            contrato = re.sub(r"\D", "", message.text)

            if len(contrato) >= 6:

                descontar_credito(message.from_user.id)
                creditos_restantes = obtener_creditos(message.from_user.id)

                bot.send_message(
                    message.chat.id,
                    f"✅ Contrato detectado:\n{contrato}\n\n"
                    f"💳 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            else:
                bot.send_message(message.chat.id, "❌ Contrato inválido")

        # -------------------------
        # INTERNET
        # -------------------------
        elif estado == "internet":

            servicio = re.sub(r"\D", "", message.text)

            if len(servicio) >= 6:

                descontar_credito(message.from_user.id)
                creditos_restantes = obtener_creditos(message.from_user.id)

                bot.send_message(
                    message.chat.id,
                    f"✅ Servicio detectado:\n{servicio}\n\n"
                    f"💳 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            else:
                bot.send_message(message.chat.id, "❌ Número inválido")
