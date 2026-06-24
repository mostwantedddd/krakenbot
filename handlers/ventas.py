import re
from database import obtener_creditos, descontar_creditos

def registrar_ventas(bot):

    estados = {}

    # -------------------------
    # COBRAR 50% CRÉDITOS
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

        descontar_creditos(message.from_user.id, creditos_a_cobrar)
        return True

    # =========================
    # RECARGAS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📱 Recargas")
    def recargas(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(message.chat.id, f"❌ No tienes créditos.\n💰 {creditos}")
            return

        estados[message.chat.id] = {
            "estado": "recarga"
        }

        bot.send_message(
            message.chat.id,
            "📱 Envía el número a recargar (10 dígitos)"
        )

    # =========================
    # MEGACABLE
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📺 Megacable")
    def megacable(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(message.chat.id, f"❌ No tienes créditos.\n💰 {creditos}")
            return

        estados[message.chat.id] = {
            "estado": "megacable"
        }

        bot.send_message(
            message.chat.id,
            "📺 Envía tu número de contrato"
        )

    # =========================
    # INTERNET
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🌐 Internet")
    def internet(message):

        creditos = obtener_creditos(message.from_user.id)

        if creditos <= 0:
            bot.send_message(message.chat.id, f"❌ No tienes créditos.\n💰 {creditos}")
            return

        estados[message.chat.id] = {
            "estado": "internet"
        }

        bot.send_message(
            message.chat.id,
            "🌐 Envía tu número de servicio"
        )

    # =========================
    # CAPTURA GENERAL
    # =========================
    @bot.message_handler(func=lambda m: m.chat.id in estados)
    def capturar(message):

        estado = estados.get(message.chat.id)

        # -------------------------
        # RECARGA → NÚMERO
        # -------------------------
        if estado["estado"] == "recarga":

            numero = re.sub(r"\D", "", message.text)

            if len(numero) == 10:

                estados[message.chat.id] = {
                    "estado": "compania_recarga",
                    "numero": numero
                }

                bot.send_message(
                    message.chat.id,
                    "📱 Escribe la compañía en minúsculas:\n"
                    "telcel, movistar, att, bait, unefon"
                )
            else:
                bot.send_message(message.chat.id, "❌ Número inválido")

        # -------------------------
        # RECARGA → COMPAÑÍA
        # -------------------------
        elif estado["estado"] == "compania_recarga":

            compania = message.text.strip()

            validas = ["telcel", "movistar", "att", "bait", "unefon"]

            if compania not in validas:
                bot.send_message(message.chat.id, "❌ Compañía inválida")
                return

            estados[message.chat.id] = {
                "estado": "monto_recarga",
                "compania": compania,
                "numero": estado["numero"]
            }

            bot.send_message(
                message.chat.id,
                "💰 Ahora envía el monto"
            )

        # -------------------------
        # RECARGA → MONTO
        # -------------------------
        elif estado["estado"] == "monto_recarga":

            try:
                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(message.chat.id, "❌ Monto inválido")
                    return

                cargando = bot.send_message(
                message.chat.id,
                "⏳ Procesando pago..."
                )

                time.sleep(5)

                if not cobrar_creditos_por_monto(message, monto):
                    estados.pop(message.chat.id)
                    return

                creditos_restantes = obtener_creditos(message.from_user.id)

                bot.send_message(
                    message.chat.id,
                    f"✅ Recarga exitosa\n\n"
                    f"📱 {estado['compania']}\n"
                    f"💵 ${monto:.2f}\n"
                    f"💸 Créditos: {max(1, int(monto/2))}\n"
                    f"💰 Restantes: {creditos_restantes}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")

        # -------------------------
        # MEGACABLE → CONTRATO
        # -------------------------
        elif estado["estado"] == "megacable":

            contrato = re.sub(r"\D", "", message.text)

            if len(contrato) < 6:
                bot.send_message(message.chat.id, "❌ Contrato inválido")
                return

            estados[message.chat.id] = {
                "estado": "monto_megacable"
            }

            bot.send_message(message.chat.id, "💰 Envía el monto")

        # -------------------------
        # MEGACABLE → MONTO
        # -------------------------
        elif estado["estado"] == "monto_megacable":

            try:
                monto = float(message.text)

                if monto <= 0:
                    bot.send_message(message.chat.id, "❌ Monto inválido")
                    return

                cargando = bot.send_message(
                message.chat.id,
                "⏳ Procesando pago..."
                )

                time.sleep(5)

                if not cobrar_creditos_por_monto(message, monto):
                    estados.pop(message.chat.id)
                    return

                bot.send_message(
                    message.chat.id,
                    f"✅ Megacable procesado\n💵 ${monto:.2f}"
                )

                estados.pop(message.chat.id)

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")
