
from threading import Lock


# =====================================================
# ESTADOS DE CONVERSACIÓN
# =====================================================

ESTADO_MENU = "menu"
ESTADO_SERVICIO = "servicio"
ESTADO_NOMBRE = "nombre"
ESTADO_CORREO = "correo"
ESTADO_FECHA = "fecha"
ESTADO_HORARIO = "horario"
ESTADO_CONFIRMACION = "confirmacion"


# =====================================================
# ALMACENAMIENTO TEMPORAL
# =====================================================

conversaciones = {}

bloqueo_conversaciones = Lock()


# =====================================================
# OBTENER CONVERSACIÓN
# =====================================================

def obtener_conversacion(remitente, id_establecimiento):

    clave = (
        str(id_establecimiento),
        str(remitente)
    )

    with bloqueo_conversaciones:

        if clave not in conversaciones:
            conversaciones[clave] = {
                "estado": ESTADO_MENU,
                "datos": {}
            }

        return conversaciones[clave]


# =====================================================
# REINICIAR CONVERSACIÓN
# =====================================================

def reiniciar_conversacion(remitente, id_establecimiento):

    clave = (
        str(id_establecimiento),
        str(remitente)
    )

    with bloqueo_conversaciones:

        conversaciones[clave] = {
            "estado": ESTADO_MENU,
            "datos": {}
        }

        return conversaciones[clave]


# =====================================================
# NORMALIZAR TELÉFONO
# =====================================================

def normalizar_telefono(telefono):

    """Normaliza teléfonos colombianos a 10 dígitos nacionales."""

    numero = "".join(
        caracter
        for caracter in str(telefono)
        if caracter.isdigit()
    )

    if numero.startswith("57") and len(numero) == 12:
        numero = numero[2:]

    return numero
    
# =====================================================
# BUSCAR CLIENTE POR TELÉFONO
# =====================================================

def buscar_cliente(remitente, id_establecimiento):

    from apps.clients import repositories

    telefono = normalizar_telefono(remitente)

    try:

        cliente = repositories.obtener_cliente_por_telefono(
            telefono,
            id_establecimiento
        )

        return {
            "ok": True,
            "cliente": cliente,
            "error": None
        }

    except Exception as error:

        print(
            f"Error al buscar cliente desde WhatsApp: {error}"
        )

        return {
            "ok": False,
            "cliente": None,
            "error": str(error)
        }
    

# =====================================================
# REGISTRAR CLIENTE DESDE WHATSAPP
# =====================================================

def registrar_cliente_whatsapp(
    remitente,
    id_establecimiento,
    nombre,
    correo=None
):

    from apps.clients.services import registrar_cliente

    telefono = normalizar_telefono(remitente)

    datos = {
        "nombre": nombre.strip(),
        "telefono": telefono,
        "correo": correo.strip() if correo else None
    }

    try:

        resultado, codigo = registrar_cliente(
            datos,
            id_establecimiento
        )

        return resultado, codigo

    except Exception as error:

        print(
            f"Error al registrar cliente desde WhatsApp: {error}"
        )

        return {
            "ok": False,
            "mensaje": "No fue posible registrar el cliente.",
            "data": None,
            "errores": {}
        }, 500
        

# =====================================================
# OBTENER SERVICIOS PARA WHATSAPP
# =====================================================

def obtener_servicios_whatsapp(id_establecimiento):

    from apps.services.services import obtener_servicios

    try:

        resultado = obtener_servicios(id_establecimiento)

        if not resultado["ok"]:
            return []

        return resultado["data"] or []

    except Exception as error:

        print(
            f"Error al consultar servicios desde WhatsApp: {error}"
        )

        return []
    

# =====================================================
# SELECCIONAR SERVICIO
# =====================================================

def seleccionar_servicio(id_establecimiento, opcion):

    servicios = obtener_servicios_whatsapp(
        id_establecimiento
    )

    try:
        indice = int(opcion) - 1

    except (ValueError, TypeError):
        return None

    if indice < 0 or indice >= len(servicios):
        return None

    return servicios[indice]


# =====================================================
# VALIDAR FECHA DE RESERVA
# =====================================================

from datetime import date, datetime


def validar_fecha_reserva(fecha):

    try:

        fecha_obj = datetime.strptime(
            str(fecha).strip(),
            "%Y-%m-%d"
        ).date()

        if fecha_obj < date.today():
            return None

        return fecha_obj.strftime("%Y-%m-%d")

    except (ValueError, TypeError):

        return None
    

# =====================================================
# OBTENER HORARIOS DISPONIBLES PARA WHATSAPP
# =====================================================

def obtener_horarios_whatsapp(
    id_establecimiento,
    id_servicio,
    fecha
):

    from apps.appointments.services import (
        consultar_horarios_disponibles
    )

    fecha_validada = validar_fecha_reserva(fecha)

    if not fecha_validada:
        return []

    try:

        resultado = consultar_horarios_disponibles(
            id_establecimiento,
            id_servicio,
            fecha_validada
        )

        if not resultado["ok"]:
            return []

        return resultado["data"]["horarios"]

    except Exception as error:

        print(
            f"Error al consultar horarios desde WhatsApp: {error}"
        )

        return []
    

# =====================================================
# SELECCIONAR HORARIO
# =====================================================

def seleccionar_horario(horarios, opcion):

    try:
        indice = int(opcion) - 1

    except (ValueError, TypeError):
        return None

    if indice < 0 or indice >= len(horarios):
        return None

    return horarios[indice]


# =====================================================
# REGISTRAR CITA DESDE WHATSAPP
# =====================================================

def registrar_cita_whatsapp(
    id_establecimiento,
    id_cliente,
    id_servicio,
    fecha,
    hora_inicio
):

    from apps.appointments.services import registrar_cita

    datos = {
        "id_cliente": id_cliente,
        "id_servicio": id_servicio,
        "fecha": fecha,
        "hora_inicio": hora_inicio
    }

    try:

        return registrar_cita(
            datos,
            id_establecimiento
        )

    except Exception as error:

        print(
            f"Error al registrar cita desde WhatsApp: {error}"
        )

        return {
            "ok": False,
            "mensaje": "No fue posible registrar la cita.",
            "data": None,
            "errores": {}
        }
        

# =====================================================
# CONSTRUIR RESUMEN DE RESERVA
# =====================================================

def construir_resumen_reserva(datos):

    cliente = datos.get("cliente", {})
    servicio = datos.get("servicio", {})
    horario = datos.get("horario", {})

    return (
        "RESUMEN DE TU RESERVA\n\n"
        f"Cliente: {cliente.get('nombre', '')}\n"
        f"Servicio: {servicio.get('nombre', '')}\n"
        f"Fecha: {datos.get('fecha', '')}\n"
        f"Hora: {horario.get('hora_inicio', '')} - "
        f"{horario.get('hora_fin', '')}\n"
        f"Duración: {servicio.get('duracion_minutos', '')} minutos\n"
        f"Precio: ${servicio.get('precio', '')}\n\n"
        "¿Deseas confirmar esta reserva?\n"
        "Responde SI para confirmar o NO para cancelar."
    )
    
    
# =====================================================
# CONSTRUIR MENÚ DE SERVICIOS
# =====================================================

def construir_menu_servicios(id_establecimiento):

    servicios = obtener_servicios_whatsapp(
        id_establecimiento
    )

    if not servicios:
        return "En este momento no tenemos servicios disponibles."

    mensaje = "¡Bienvenido a CitaFácil!\n\n"
    mensaje += "Estos son nuestros servicios disponibles:\n\n"

    for indice, servicio in enumerate(servicios, start=1):

        mensaje += (
            f"{indice}. {servicio['nombre']}\n"
            f"   Duración: {servicio['duracion_minutos']} minutos\n"
            f"   Precio: ${servicio['precio']}\n\n"
        )

    mensaje += (
        "Responde con el número del servicio que deseas reservar.\n\n"
        "Escribe MENU en cualquier momento para volver al inicio."
    )

    return mensaje


# =====================================================
# SOLICITAR NOMBRE DEL CLIENTE
# =====================================================

def construir_solicitud_nombre():

    return (
        "¡Perfecto! Vamos a realizar tu reserva.\n\n"
        "Para continuar, por favor escribe tu nombre completo."
    )
    
    
# =====================================================
# SOLICITAR CORREO DEL CLIENTE
# =====================================================

def construir_solicitud_correo():

    return (
        "¡Gracias!\n\n"
        "Ahora escribe tu correo electrónico.\n\n"
        "Si no deseas proporcionar uno, responde 0."
    )
    
    
# =====================================================
# SOLICITAR FECHA DE LA RESERVA
# =====================================================

def construir_solicitud_fecha():

    return (
        "¡Excelente! Ahora seleccionemos la fecha de tu cita.\n\n"
        "Escribe la fecha que deseas en el siguiente formato:\n"
        "AAAA-MM-DD\n\n"
        "Ejemplo: 2026-11-16"
    )
    
    
# =====================================================
# CONSTRUIR MENÚ DE HORARIOS
# =====================================================

def construir_menu_horarios(horarios):

    if not horarios:
        return (
            "Lo sentimos, no hay horarios disponibles "
            "para esta fecha.\n\n"
            "Por favor, intenta con otra fecha."
        )

    mensaje = "Estos son los horarios disponibles:\n\n"

    for indice, horario in enumerate(horarios, start=1):

        mensaje += (
            f"{indice}. "
            f"{horario['hora_inicio']} - "
            f"{horario['hora_fin']}\n"
        )

    mensaje += (
        "\nResponde con el número del horario que prefieres."
    )

    return mensaje


# =====================================================
# MENSAJE DE CONFIRMACIÓN
# =====================================================

def construir_mensaje_confirmacion():

    return (
        "¿Deseas confirmar esta reserva?\n\n"
        "Responde:\n"
        "1. Sí, confirmar mi cita.\n"
        "2. No, cancelar la reserva."
    )
    
    
# =====================================================
# MENSAJE DE RESERVA EXITOSA
# =====================================================

def construir_mensaje_reserva_exitosa(resultado):

    data = resultado.get("data", {})

    return (
        "¡Tu cita ha sido registrada correctamente!\n\n"
        f"Número de cita: {data.get('id_cita', '')}\n"
        f"Fecha: {data.get('fecha', '')}\n"
        f"Hora: {data.get('hora_inicio', '')} - "
        f"{data.get('hora_fin', '')}\n\n"
        "¡Gracias por elegir CitaFácil!"
    )
    
    
# =====================================================
# MENSAJE DE RESERVA CANCELADA
# =====================================================

def construir_mensaje_reserva_cancelada():

    return (
        "Tu reserva ha sido cancelada.\n\n"
        "No se ha registrado ninguna cita.\n\n"
        "Si deseas realizar una nueva reserva, "
        "escribe MENU."
    )
    

# =====================================================
# REGISTRAR Y OBTENER CLIENTE DESDE WHATSAPP
# =====================================================

def procesar_registro_cliente(
    remitente,
    id_establecimiento,
    nombre,
    correo=None
):

    resultado, codigo = registrar_cliente_whatsapp(
        remitente,
        id_establecimiento,
        nombre,
        correo
    )

    if not resultado.get("ok"):

        return {
            "ok": False,
            "mensaje": resultado.get(
                "mensaje",
                "No fue posible registrar el cliente."
            ),
            "cliente": None
        }

    cliente = resultado.get("data") or {}

    if not cliente.get("id_cliente"):

        return {
            "ok": False,
            "mensaje": "No fue posible recuperar el cliente registrado.",
            "cliente": None
        }

    return {
        "ok": True,
        "mensaje": resultado.get("mensaje"),
        "cliente": cliente
    }
    

# =====================================================
# INICIAR RESERVA DESDE WHATSAPP
# =====================================================

def iniciar_reserva(remitente, id_establecimiento):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    conversacion["estado"] = ESTADO_SERVICIO
    conversacion["datos"] = {}

    return construir_menu_servicios(
        id_establecimiento
    )


# =====================================================
# PROCESAR SELECCIÓN DE SERVICIO
# =====================================================

def procesar_seleccion_servicio(
    remitente,
    id_establecimiento,
    opcion
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    servicio = seleccionar_servicio(
        id_establecimiento,
        opcion
    )

    if not servicio:

        return {
            "ok": False,
            "mensaje": "Opción inválida. Por favor, selecciona un servicio del menú."
        }

    conversacion["datos"]["servicio"] = servicio

    resultado_busqueda = buscar_cliente(
        remitente,
        id_establecimiento
    )

    if not resultado_busqueda["ok"]:

        return {
            "ok": False,
            "mensaje": "No fue posible consultar tus datos. Inténtalo nuevamente."
        }

    cliente = resultado_busqueda["cliente"]

    if cliente:

        conversacion["datos"]["cliente"] = cliente
        conversacion["estado"] = ESTADO_FECHA

        return {
            "ok": True,
            "mensaje": construir_solicitud_fecha()
        }

    conversacion["estado"] = ESTADO_NOMBRE

    return {
        "ok": True,
        "mensaje": construir_solicitud_nombre()
    }
    

# =====================================================
# PROCESAR NOMBRE DEL CLIENTE
# =====================================================

def procesar_nombre_cliente(
    remitente,
    id_establecimiento,
    nombre
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    nombre = nombre.strip()

    if len(nombre) < 3:

        return {
            "ok": False,
            "mensaje": "Por favor, escribe tu nombre completo."
        }

    conversacion["datos"]["nombre"] = nombre
    conversacion["estado"] = ESTADO_CORREO

    return {
        "ok": True,
        "mensaje": construir_solicitud_correo()
    }
    

# =====================================================
# PROCESAR CORREO Y REGISTRAR CLIENTE
# =====================================================

def procesar_correo_cliente(
    remitente,
    id_establecimiento,
    correo
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    correo = correo.strip()

    if correo.lower() in ("0", "omitir"):

        correo = None

    elif correo:

        import re

        patron = r"^[^@\s]+@[^@\s]+**\\.**[^@\s]+$"

        if not re.match(patron, correo):

            return {
                "ok": False,
                "mensaje": "El correo no tiene un formato válido. Escríbelo nuevamente o responde 0 para omitirlo."
            }

    nombre = conversacion["datos"].get("nombre")

    resultado = procesar_registro_cliente(
        remitente,
        id_establecimiento,
        nombre,
        correo
    )

    if not resultado["ok"]:

        return {
            "ok": False,
            "mensaje": resultado["mensaje"]
        }

    conversacion["datos"]["cliente"] = resultado["cliente"]
    conversacion["estado"] = ESTADO_FECHA

    return {
        "ok": True,
        "mensaje": construir_solicitud_fecha()
    }
    
    
# =====================================================
# PROCESAR FECHA DE RESERVA
# =====================================================

def procesar_fecha_reserva(
    remitente,
    id_establecimiento,
    fecha
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    fecha_validada = validar_fecha_reserva(fecha.strip())

    if not fecha_validada:

        return {
            "ok": False,
            "mensaje": "La fecha no es válida o ya pasó. Utiliza el formato AAAA-MM-DD."
        }

    servicio = conversacion["datos"].get("servicio")

    if not servicio:

        return {
            "ok": False,
            "mensaje": "No se encontró el servicio seleccionado. Inicia nuevamente la reserva."
        }

    horarios = obtener_horarios_whatsapp(
        id_establecimiento,
        servicio["id_servicio"],
        fecha_validada
    )

    if not horarios:

        return {
            "ok": False,
            "mensaje": "No hay horarios disponibles para esa fecha. Por favor, selecciona otra fecha."
        }

    conversacion["datos"]["fecha"] = fecha_validada
    conversacion["datos"]["horarios_disponibles"] = horarios
    conversacion["estado"] = ESTADO_HORARIO

    return {
        "ok": True,
        "mensaje": construir_menu_horarios(horarios)
    }
    

# =====================================================
# PROCESAR SELECCIÓN DE HORARIO
# =====================================================

def procesar_seleccion_horario(
    remitente,
    id_establecimiento,
    opcion
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    servicio = conversacion["datos"].get("servicio")
    fecha = conversacion["datos"].get("fecha")

    if not servicio or not fecha:

        return {
            "ok": False,
            "mensaje": "Faltan datos de la reserva. Inicia nuevamente el proceso."
        }

    horarios = conversacion["datos"].get("horarios_disponibles", [])

    horario = seleccionar_horario(
        horarios,
        opcion
    )

    if not horario:

        return {
            "ok": False,
            "mensaje": "Opción de horario inválida. Selecciona un horario de la lista."
        }

    conversacion["datos"]["horario"] = horario
    conversacion["estado"] = ESTADO_CONFIRMACION

    return {
        "ok": True,
        "mensaje": construir_resumen_reserva(
            conversacion["datos"]
        )
    }
    

# =====================================================
# PROCESAR CONFIRMACIÓN DE RESERVA
# =====================================================

def procesar_confirmacion_reserva(
    remitente,
    id_establecimiento,
    respuesta
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    respuesta = respuesta.strip().lower()

    if respuesta in ("2", "no", "cancelar"):

        reiniciar_conversacion(
            remitente,
            id_establecimiento
        )

        return {
            "ok": True,
            "mensaje": construir_mensaje_reserva_cancelada()
        }

    if respuesta not in ("1", "si", "sí", "confirmar"):

        return {
            "ok": False,
            "mensaje": "Respuesta no válida. Escribe 1 para confirmar o 2 para cancelar."
        }

    datos = conversacion["datos"]

    cliente = datos.get("cliente")
    servicio = datos.get("servicio")
    fecha = datos.get("fecha")
    horario = datos.get("horario")

    if not cliente or not servicio or not fecha or not horario:

        return {
            "ok": False,
            "mensaje": "Faltan datos para registrar la reserva. Inicia nuevamente el proceso."
        }

    resultado = registrar_cita_whatsapp(
        id_establecimiento,
        cliente["id_cliente"],
        servicio["id_servicio"],
        fecha,
        horario["hora_inicio"]
    )

    if not resultado.get("ok"):

        errores = resultado.get("errores") or {}

        if "hora_inicio" in errores:

            horarios = obtener_horarios_whatsapp(
                id_establecimiento,
                servicio["id_servicio"],
                fecha
            )

            conversacion["datos"]["horarios_disponibles"] = horarios
            conversacion["datos"].pop("horario", None)

            if horarios:

                conversacion["estado"] = ESTADO_HORARIO

                return {
                    "ok": False,
                    "mensaje": (
                        "El horario seleccionado acaba de ocuparse.\n\n"
                        "Estos son los horarios actualizados:\n\n"
                        + construir_menu_horarios(horarios)
                    )
                }

            conversacion["estado"] = ESTADO_FECHA
            conversacion["datos"].pop("fecha", None)
            conversacion["datos"].pop("horarios_disponibles", None)

            return {
                "ok": False,
                "mensaje": (
                    "El horario seleccionado acaba de ocuparse "
                    "y ya no quedan horarios disponibles para esa fecha.\n\n"
                    "Por favor, selecciona otra fecha."
                )
            }

        return {
            "ok": False,
            "mensaje": resultado.get(
                "mensaje",
                "No fue posible registrar la reserva. Inténtalo nuevamente."
            )
        }

    mensaje = construir_mensaje_reserva_exitosa(resultado)

    reiniciar_conversacion(
        remitente,
        id_establecimiento
    )

    return {
        "ok": True,
        "mensaje": mensaje
    }
    
    
# =====================================================
# PROCESAR MENSAJES DE WHATSAPP
# =====================================================

def procesar_mensaje(
    remitente,
    id_establecimiento,
    mensaje
):

    conversacion = obtener_conversacion(
        remitente,
        id_establecimiento
    )

    mensaje = (mensaje or "").strip()

    if not mensaje:

        return {
            "ok": False,
            "mensaje": "Por favor, escribe un mensaje."
        }

    comando = mensaje.lower()

    # Comandos generales
    if comando in ("cancelar", "reiniciar", "menu"):

        reiniciar_conversacion(
            remitente,
            id_establecimiento
        )

        if comando == "cancelar":

            return {
                "ok": True,
                "mensaje": construir_mensaje_reserva_cancelada()
            }

        return {
            "ok": True,
            "mensaje": "Bienvenido a CitaFácil.\nEscribe 1 para iniciar una reserva."
        }

    estado = conversacion["estado"]

    # Selección del servicio
    if estado == ESTADO_MENU:

        if comando in ("1", "reservar", "iniciar"):

            return {
                "ok": True,
                "mensaje": iniciar_reserva(
                    remitente,
                    id_establecimiento
                )
            }

        return {
            "ok": True,
            "mensaje": "Bienvenido a CitaFácil.\nEscribe 1 para iniciar una reserva."
        }

    if estado == ESTADO_SERVICIO:

        return procesar_seleccion_servicio(
            remitente,
            id_establecimiento,
            mensaje
        )

    # Registro del cliente
    if estado == ESTADO_NOMBRE:

        return procesar_nombre_cliente(
            remitente,
            id_establecimiento,
            mensaje
        )

    if estado == ESTADO_CORREO:

        return procesar_correo_cliente(
            remitente,
            id_establecimiento,
            mensaje
        )

    # Selección de fecha y horario
    if estado == ESTADO_FECHA:

        return procesar_fecha_reserva(
            remitente,
            id_establecimiento,
            mensaje
        )

    if estado == ESTADO_HORARIO:

        return procesar_seleccion_horario(
            remitente,
            id_establecimiento,
            mensaje
        )

    # Confirmación final
    if estado == ESTADO_CONFIRMACION:

        return procesar_confirmacion_reserva(
            remitente,
            id_establecimiento,
            mensaje
        )

    reiniciar_conversacion(
        remitente,
        id_establecimiento
    )

    return {
        "ok": False,
        "mensaje": "La conversación se reinició. Escribe 1 para iniciar una reserva."
    }
    

