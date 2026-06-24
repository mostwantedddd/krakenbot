import re
from database import obtener_creditos, descontar_creditos

def registrar_ventas(bot):

    estados = {}

    # -------------------------
    # FUNCIÓN PARA COBRAR CRÉDITOS
    # -------------------------
    def cobrar_creditos_por_monto(message, monto):

        creditos_a_cobrar = max(1, int(monto / 2))

        creditos_actuales = obtener_creditos(message.from_user.id)

        if creditos_actuales < creditos_a_cobrar:

            bot.send_message(
                message.chat.id,
                f"❌ Créditos insuficientes.\n\n"
                f"Necesitas: {creditos_a_cobrar}\n"
                f"Tienes: {creditos_actuales}"
            )

            return False

        descontar_creditos(
            message.from_user.id,
            creditos_a_cobrar
        )

        return True

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
    # CAPTURA DE MENSAJES
    # -------------------------
    @bot.message_handler(func=lambda m: m.chat.id in estados)
    def capturar(message):

        estado = estados.get(message.chat.id)

        # -------------------------
        # RECARGA: PEDIR NÚMERO
        # -------------------------
        if estado == "recarga":

    numero = re.sub(r"\D", "", message.text)

    if len(numero) == 10:

        estados[message.chat.id] = {
            "estado": "compania_recarga",
            "numero": numero
        }

        bot.send_message(
            message.chat.id,
            "✅ Número detectado.\n\n"
            "Escribe la compañía en minúsculas:\n\n"
            "• telcel\n"
            "• movistar\n"
            "• att\n"
            "• bait\n"
            "• unefon"
        )

    else:
        bot.send_message(
            message.chat.id,
            "❌ Debe tener 10 dígitos."
        )

        # -------------------------
        # RECARGA: PEDIR MONTO
        # -------------------------
        elif isinstance(estado, dict) and estado["estado"] == "compania_recarga":

    companias_validas = [
        "telcel",
        "movistar",
        "att",
        "bait",
        "unefon"
    ]

    compania = message.text.strip()

    if compania not in companias_validas:

        bot.send_message(
            message.chat.id,
            "❌ Compañía inválida.\n\n"
            "Debes escribir exactamente:\n"
            "telcel, movistar, att, bait o unefon"
        )
        return

    estados[message.chat.id] = {
        "estado": "monto_recarga",
        "compania": compania
    }

    bot.send_message(
        message.chat.id,
        f"✅ Compañía detectada: {compania}\n\n"
        "Ahora envía el monto."
    )
        elif isinstance(estado, dict) and estado["estado"] == "monto_recarga":

            try:

                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(
                        message.chat.id,
                        "❌ Monto inválido"
                    )
                    return

                if not cobrar_creditos_por_monto(message, monto):
                    estados.pop(message.chat.id, None)
                    return

                creditos_restantes = obtener_creditos(
                    message.from_user.id
                )

                compania = estado["compania"]

                bot.send_message(
    message.chat.id,
    f"✅ Recarga procesada\n\n"
    f"📱 Compañía: {compania}\n"
    f"💵 Monto: ${monto:.2f}\n"
    f"💸 Créditos cobrados: {max(1, int(monto / 2))}\n"
    f"💰 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ Envía un monto válido"
                )

        # -------------------------
        # MEGACABLE: PEDIR CONTRATO
        # -------------------------
        elif estado == "megacable":

            contrato = re.sub(r"\D", "", message.text)

            if len(contrato) >= 6:

                estados[message.chat.id] = "monto_megacable"

                bot.send_message(
                    message.chat.id,
                    f"✅ Contrato detectado: {contrato}\n\n"
                    "Ahora envía el monto a pagar."
                )

            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Contrato inválido"
                )

        # -------------------------
        # MEGACABLE: PEDIR MONTO
        # -------------------------
        elif estado == "monto_megacable":

            try:

                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(
                        message.chat.id,
                        "❌ Monto inválido"
                    )
                    return

                if not cobrar_creditos_por_monto(message, monto):
                    estados.pop(message.chat.id, None)
                    return

                creditos_restantes = obtener_creditos(
                    message.from_user.id
                )

                bot.send_message(
                    message.chat.id,
                    f"✅ Pago Megacable procesado\n\n"
                    f"💵 Monto: ${monto:.2f}\n"
                    f"💸 Créditos cobrados: {max(1, int(monto / 2))}\n"
                    f"💰 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ Envía un monto válido"
                )

        # -------------------------
        # INTERNET: PEDIR SERVICIO
        # -------------------------
        elif estado == "internet":

            servicio = re.sub(r"\D", "", message.text)

            if len(servicio) >= 6:

                estados[message.chat.id] = "monto_internet"

                bot.send_message(
                    message.chat.id,
                    f"✅ Servicio detectado: {servicio}\n\n"
                    "Ahora envía el monto a pagar."
                )

            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Número inválido"
                )

        # -------------------------
        # INTERNET: PEDIR MONTO
        # -------------------------
        elif estado == "monto_internet":

            try:

                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(
                        message.chat.id,
                        "❌ Monto inválido"
                    )
                    return

                if not cobrar_creditos_por_monto(message, monto):
                    estados.pop(message.chat.id, None)
                    return

                creditos_restantes = obtener_creditos(
                    message.from_user.id
                )

                bot.send_message(
                    message.chat.id,
                    f"✅ Pago Internet procesado\n\n"
                    f"💵 Monto: ${monto:.2f}\n"
                    f"💸 Créditos cobrados: {max(1, int(monto / 2))}\n"
                    f"💰 Créditos restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ Envía un monto válido"
                )
