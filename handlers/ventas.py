import re
import time
import threading
from database import obtener_creditos, descontar_creditos

def registrar_ventas(bot):

    estados = {}

    # -------------------------
    # COBRAR 50% CRÉDITOS
    # -------------------------
    def cobrar_creditos_por_monto(user_id, chat_id, monto):
        creditos_a_cobrar = max(1, int(monto / 2))
        creditos_actuales = obtener_creditos(user_id)

        if creditos_actuales < creditos_a_cobrar:
            bot.send_message(
                chat_id,
                f"❌ Créditos insuficientes.\n\n"
                f"Necesitas: {creditos_a_cobrar}\n"
                f"Tienes: {creditos_actuales}"
            )
            return False

        descontar_creditos(user_id, creditos_a_cobrar)
        return True

    # =========================
    # RECARGAS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📱 Recargas")
    def recargas(message):
        # Si ya hay un proceso activo, mostrar tiempo restante y salir
        if message.chat.id in estados and estados[message.chat.id].get("estado") == "procesando":
            inicio = estados[message.chat.id]["inicio"]
            ahora = time.time()
            if ahora - inicio < 60:
                restante = int(60 - (ahora - inicio))
                bot.send_message(message.chat.id, f"⏳ Aún procesando...\n⏱ Espera {restante} segundos")
                return
            else:
                estados.pop(message.chat.id, None)

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
        if message.chat.id in estados and estados[message.chat.id].get("estado") == "procesando":
            inicio = estados[message.chat.id]["inicio"]
            ahora = time.time()
            if ahora - inicio < 60:
                restante = int(60 - (ahora - inicio))
                bot.send_message(message.chat.id, f"⏳ Aún procesando...\n⏱ Espera {restante} segundos")
                return
            else:
                estados.pop(message.chat.id, None)

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
        if message.chat.id in estados and estados[message.chat.id].get("estado") == "procesando":
            inicio = estados[message.chat.id]["inicio"]
            ahora = time.time()
            if ahora - inicio < 60:
                restante = int(60 - (ahora - inicio))
                bot.send_message(message.chat.id, f"⏳ Aún procesando...\n⏱ Espera {restante} segundos")
                return
            else:
                estados.pop(message.chat.id, None)

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
        if not estado:
            return

        # -------------------------
        # PROCESANDO PAGO (Timer activo)
        # -------------------------
        if estado["estado"] == "procesando":
            inicio = estado["inicio"]
            ahora = time.time()
            if ahora - inicio < 60:
                restante = int(60 - (ahora - inicio))
                bot.send_message(
                    message.chat.id,
                    f"⏳ Aún procesando...\n⏱ Espera {restante} segundos"
                )
            else:
                # Si ya pasaron los 60s y el Timer no limpió, forzamos limpieza
                bot.send_message(message.chat.id, "✅ El pago ya debería haberse completado. Intenta de nuevo.")
                estados.pop(message.chat.id, None)
            return

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
            compania = message.text.strip().lower()
            validas = ["telcel", "movistar", "att", "bait", "unefon"]
            if compania not in validas:
                bot.send_message(message.chat.id, "❌ Compañía inválida")
                return
            estados[message.chat.id] = {
                "estado": "monto_recarga",
                "compania": compania,
                "numero": estado["numero"]
            }
            bot.send_message(message.chat.id, "💰 Ahora envía el monto")

        # -------------------------
        # RECARGA → MONTO
        # -------------------------
        elif estado["estado"] == "monto_recarga":
            try:
                monto = float(message.text)
                if monto <= 0:
                    bot.send_message(message.chat.id, "❌ Monto inválido")
                    return

                # Guardar estado de procesamiento y lanzar Timer
                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_recarga",
                    "compania": estado["compania"],
                    "numero": estado["numero"]
                }

                def procesar_recarga(chat_id, user_id, monto, compania, numero):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    creditos_restantes = obtener_creditos(user_id)
                    bot.send_message(
                        chat_id,
                        f"✅ Recarga exitosa . . . . OK\n\n"
                        f"📱 {compania}\n"
                        f"💵 ${monto:.2f}\n"
                        f"💸 Créditos: {max(1, int(monto/2))}\n"
                        f"💰 Restantes: {creditos_restantes}"
                    )
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_recarga,
                                args=(message.chat.id, message.from_user.id, monto,
                                      estado["compania"], estado["numero"])).start()

                bot.send_message(message.chat.id, "⏳ Pago en proceso... espera 60 segundos")

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

                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_megacable",
                    "contrato": contrato if 'contrato' in estado else "N/A"
                }

                def procesar_megacable(chat_id, user_id, monto):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    bot.send_message(
                        chat_id,
                        f"✅ Megacable procesado\n\n"
                        f"💵 ${monto:.2f}\n"
                        f"💸 Créditos cobrados: {max(1, int(monto/2))}"
                    )
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_megacable,
                                args=(message.chat.id, message.from_user.id, monto)).start()

                bot.send_message(message.chat.id, "⏳ Pago en proceso... espera 60 segundos")

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")

        # -------------------------
        # INTERNET → MONTO (flujo completo internet no estaba en el original, lo agrego para que sea consistente)
        # -------------------------
        elif estado["estado"] == "internet":
            servicio = message.text.strip()
            if not servicio:
                bot.send_message(message.chat.id, "❌ Número de servicio inválido")
                return
            estados[message.chat.id] = {
                "estado": "monto_internet",
                "servicio": servicio
            }
            bot.send_message(message.chat.id, "💰 Envía el monto")

        elif estado["estado"] == "monto_internet":
            try:
                monto = float(message.text)
                if monto <= 0:
                    bot.send_message(message.chat.id, "❌ Monto inválido")
                    return

                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_internet",
                    "servicio": estado["servicio"]
                }

                def procesar_internet(chat_id, user_id, monto, servicio):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    bot.send_message(
                        chat_id,
                        f"✅ Internet procesado\n\n"
                        f"🌐 Servicio: {servicio}\n"
                        f"💵 ${monto:.2f}\n"
                        f"💸 Créditos cobrados: {max(1, int(monto/2))}"
                    )
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_internet,
                                args=(message.chat.id, message.from_user.id, monto, estado["servicio"])).start()

                bot.send_message(message.chat.id, "⏳ Pago en proceso... espera 60 segundos")

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")
