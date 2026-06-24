import re
import time
import threading
import random
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

    # Función para generar un ticket con todos los datos
    def generar_ticket(user_id, tipo, datos_servicio, monto, creditos_usados, estado_pago="✅ Completado"):
        folio = f"TX-{int(time.time())}-{random.randint(1000,9999)}"
        fecha_hora = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        lineas = [
            f"🎫 *Ticket de compra*",
            f"📌 Folio: `{folio}`",
            f"📅 Fecha: {fecha_hora}",
            f"👤 Usuario ID: `{user_id}`",
            f"📦 Servicio: {tipo}",
            f"📋 Datos: {datos_servicio}",
            f"💰 Monto: ${monto:.2f}",
            f"💸 Créditos usados: {creditos_usados}",
            f"📌 Estado: {estado_pago}"
        ]
        return "\n".join(lineas)

    # =========================
    # RECARGAS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📱 Recargas")
    def recargas(message):
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

                creditos_a_usar = max(1, int(monto/2))

                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_recarga",
                    "compania": estado["compania"],
                    "numero": estado["numero"],
                    "creditos_a_usar": creditos_a_usar
                }

                def procesar_recarga(chat_id, user_id, monto, compania, numero, creditos_usados):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    creditos_restantes = obtener_creditos(user_id)
                    ticket = generar_ticket(
                        user_id=user_id,
                        tipo="📱 Recarga",
                        datos_servicio=f"{compania} - {numero}",
                        monto=monto,
                        creditos_usados=creditos_usados
                    )
                    mensaje = f"✅ Recarga exitosa\n\n{ticket}\n\n💰 Créditos restantes: {creditos_restantes}"
                    bot.send_message(chat_id, mensaje)
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_recarga,
                                args=(message.chat.id, message.from_user.id, monto,
                                      estado["compania"], estado["numero"], creditos_a_usar)).start()

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
                "estado": "monto_megacable",
                "contrato": contrato
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

                creditos_a_usar = max(1, int(monto/2))
                contrato = estado.get("contrato", "N/A")

                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_megacable",
                    "contrato": contrato,
                    "creditos_a_usar": creditos_a_usar
                }

                def procesar_megacable(chat_id, user_id, monto, contrato, creditos_usados):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    creditos_restantes = obtener_creditos(user_id)
                    ticket = generar_ticket(
                        user_id=user_id,
                        tipo="📺 Megacable",
                        datos_servicio=f"Contrato: {contrato}",
                        monto=monto,
                        creditos_usados=creditos_usados
                    )
                    mensaje = f"✅ Megacable procesado\n\n{ticket}\n\n💰 Créditos restantes: {creditos_restantes}"
                    bot.send_message(chat_id, mensaje)
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_megacable,
                                args=(message.chat.id, message.from_user.id, monto,
                                      contrato, creditos_a_usar)).start()

                bot.send_message(message.chat.id, "⏳ Pago en proceso... espera 60 segundos")

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")

        # -------------------------
        # INTERNET → MONTO
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

                creditos_a_usar = max(1, int(monto/2))
                servicio = estado["servicio"]

                estados[message.chat.id] = {
                    "estado": "procesando",
                    "inicio": time.time(),
                    "user_id": message.from_user.id,
                    "monto": monto,
                    "tipo": "monto_internet",
                    "servicio": servicio,
                    "creditos_a_usar": creditos_a_usar
                }

                def procesar_internet(chat_id, user_id, monto, servicio, creditos_usados):
                    if not cobrar_creditos_por_monto(user_id, chat_id, monto):
                        estados.pop(chat_id, None)
                        return
                    creditos_restantes = obtener_creditos(user_id)
                    ticket = generar_ticket(
                        user_id=user_id,
                        tipo="🌐 Internet",
                        datos_servicio=f"Servicio: {servicio}",
                        monto=monto,
                        creditos_usados=creditos_usados
                    )
                    mensaje = f"✅ Internet procesado\n\n{ticket}\n\n💰 Créditos restantes: {creditos_restantes}"
                    bot.send_message(chat_id, mensaje)
                    estados.pop(chat_id, None)

                threading.Timer(60.0, procesar_internet,
                                args=(message.chat.id, message.from_user.id, monto,
                                      servicio, creditos_a_usar)).start()

                bot.send_message(message.chat.id, "⏳ Pago en proceso... espera 60 segundos")

            except ValueError:
                bot.send_message(message.chat.id, "❌ Monto inválido")                     
