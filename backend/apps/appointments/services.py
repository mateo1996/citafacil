
from datetime import date, datetime, time, timedelta

from apps.appointments import repositories

from apps.appointments.serializers import (
    validar_datos_cita,
    validar_datos_estado,
    validar_identificador,
    validar_fecha,
    validar_hora,
    serializar_cita,
    serializar_citas,
    serializar_citas_usuario
)


# =====================================================
# RESPUESTA DEL SERVICIO
# =====================================================

def respuesta(ok, mensaje, data=None, errores=None):
    return {
        "ok": ok,
        "mensaje": mensaje,
        "data": data,
        "errores": errores or {}
    }


# =====================================================
# LISTAR CITAS
# =====================================================

def listar_citas(
    id_establecimiento,
    fecha_desde=None,
    fecha_hasta=None,
    estado=None
):

    citas = repositories.obtener_citas_por_establecimiento(
        id_establecimiento,
        fecha_desde,
        fecha_hasta,
        estado
    )

    return respuesta(
        True,
        "Citas consultadas correctamente.",
        serializar_citas(citas)
    )


# =====================================================
# LISTAR CITAS DE UN CLIENTE
# =====================================================

def listar_citas_usuario(id_usuario):
    """Obtiene las citas asociadas a un usuario."""

    citas = repositories.obtener_citas_por_usuario(
        id_usuario
    )

    citas_serializadas = serializar_citas_usuario(citas)

    return respuesta(
        True,
        "Tus citas fueron consultadas correctamente.",
        citas_serializadas
    )


# =====================================================
# CONSULTAR PRÓXIMAS CITAS
# =====================================================

def listar_proximas_citas(id_establecimiento, limite=5):

    citas = repositories.obtener_proximas_citas(
        id_establecimiento,
        limite
    )

    return respuesta(
        True,
        "Próximas citas consultadas correctamente.",
        serializar_citas(citas)
    )


# =====================================================
# CONSULTAR UNA CITA
# =====================================================

def consultar_cita(id_cita, id_establecimiento):

    cita = repositories.obtener_cita_por_id(
        id_cita,
        id_establecimiento
    )

    if not cita:
        return respuesta(
            False,
            "No se encontró la cita solicitada."
        )

    return respuesta(
        True,
        "Cita consultada correctamente.",
        serializar_cita(cita)
    )


# =====================================================
# CONVERTIR FECHA Y HORA
# =====================================================

def convertir_fecha_hora(fecha, hora):
    """Convierte una fecha y hora en un objeto datetime."""

    if isinstance(fecha, datetime):
        fecha_obj = fecha.date()

    elif isinstance(fecha, date):
        fecha_obj = fecha

    else:
        fecha_obj = datetime.strptime(
            str(fecha),
            "%Y-%m-%d"
        ).date()

    if isinstance(hora, datetime):
        hora_obj = hora.time()

    elif isinstance(hora, time):
        hora_obj = hora

    elif isinstance(hora, timedelta):

        segundos = int(hora.total_seconds())

        if segundos < 0 or segundos >= 86400:
            raise ValueError(
                "La hora está fuera del rango permitido."
            )

        horas, resto = divmod(segundos, 3600)
        minutos, segundos = divmod(resto, 60)

        hora_obj = time(
            horas,
            minutos,
            segundos
        )

    elif isinstance(hora, str):

        try:
            hora_obj = datetime.strptime(
                hora,
                "%H:%M"
            ).time()

        except ValueError:
            hora_obj = datetime.strptime(
                hora,
                "%H:%M:%S"
            ).time()

    else:
        raise ValueError(
            "Formato de hora no válido."
        )

    return datetime.combine(
        fecha_obj,
        hora_obj
    )


# =====================================================
# VALIDAR FECHA Y HORA FUTURA
# =====================================================

def validar_fecha_hora_futura(fecha, hora_inicio):
    """Comprueba que la cita no esté programada en el pasado."""

    try:
        inicio_cita = convertir_fecha_hora(
            fecha,
            hora_inicio
        )

        if inicio_cita <= datetime.now():
            return {
                "hora_inicio": (
                    "La fecha y hora de la cita deben ser futuras."
                )
            }

    except (ValueError, TypeError):
        return {
            "hora_inicio": (
                "La fecha o la hora no son válidas."
            )
        }

    return {}


# =====================================================
# OBTENER DÍA DE LA SEMANA
# =====================================================

def obtener_dia_semana(fecha):
    """Obtiene el nombre del día correspondiente a una fecha."""

    if isinstance(fecha, datetime):
        fecha_obj = fecha.date()

    elif isinstance(fecha, date):
        fecha_obj = fecha

    else:
        fecha_obj = datetime.strptime(
            str(fecha),
            "%Y-%m-%d"
        ).date()

    dias = [
        "lunes",
        "martes",
        "miercoles",
        "jueves",
        "viernes",
        "sabado",
        "domingo"
    ]

    return dias[fecha_obj.weekday()]


# =====================================================
# VALIDAR HORARIO DEL ESTABLECIMIENTO
# =====================================================

def validar_horario_establecimiento(
    id_establecimiento,
    fecha,
    hora_inicio,
    hora_fin
):
    """Comprueba que la cita respete el horario y descanso."""

    dia = obtener_dia_semana(fecha)

    horario = repositories.obtener_horario_por_dia(
        id_establecimiento,
        dia
    )

    if not horario:
        return {
            "horario": (
                "El establecimiento no tiene un horario "
                "activo para este día."
            )
        }

    if not horario.get("estado"):
        return {
            "horario": (
                "El establecimiento no atiende "
                "este día."
            )
        }

    try:
        inicio_cita = convertir_fecha_hora(
            fecha,
            hora_inicio
        )

        fin_cita = convertir_fecha_hora(
            fecha,
            hora_fin
        )

        inicio_atencion = convertir_fecha_hora(
            fecha,
            horario["hora_inicio"]
        )

        fin_atencion = convertir_fecha_hora(
            fecha,
            horario["hora_fin"]
        )

    except (ValueError, TypeError, KeyError):
        return {
            "horario": (
                "No fue posible interpretar el horario "
                "del establecimiento."
            )
        }

    # VALIDAR INTERVALO DE LA CITA

    if inicio_cita >= fin_cita:
        return {
            "hora_fin": (
                "La hora de finalización debe ser posterior "
                "a la hora de inicio."
            )
        }

    # VALIDAR APERTURA Y CIERRE

    if (
        inicio_cita < inicio_atencion
        or fin_cita > fin_atencion
    ):
        return {
            "horario": (
                "La cita debe encontrarse dentro "
                "del horario de atención."
            )
        }

    # VALIDAR DESCANSO

    inicio_descanso = horario.get(
        "hora_inicio_descanso"
    )

    fin_descanso = horario.get(
        "hora_fin_descanso"
    )

    if (
        inicio_descanso is not None
        and fin_descanso is not None
    ):

        try:
            inicio_descanso = convertir_fecha_hora(
                fecha,
                inicio_descanso
            )

            fin_descanso = convertir_fecha_hora(
                fecha,
                fin_descanso
            )

        except (ValueError, TypeError):
            return {
                "descanso": (
                    "No fue posible interpretar "
                    "el horario de descanso."
                )
            }

        if (
            inicio_cita < fin_descanso
            and fin_cita > inicio_descanso
        ):
            return {
                "descanso": (
                    "La cita coincide con el horario de descanso."
                )
            }

    return {}


# =====================================================
# VALIDAR DISPONIBILIDAD COMPLETA
# =====================================================

def validar_disponibilidad(
    id_establecimiento,
    fecha,
    hora_inicio,
    hora_fin,
    id_cita=None
):
    """Valida horario, descanso y conflictos con otras citas."""

    errores = validar_horario_establecimiento(
        id_establecimiento,
        fecha,
        hora_inicio,
        hora_fin
    )

    if errores:
        return errores

    conflicto = repositories.existe_conflicto_horario(
        id_establecimiento,
        fecha,
        hora_inicio,
        hora_fin,
        id_cita
    )

    if conflicto:
        return {
            "hora_inicio": (
                "El horario seleccionado ya está ocupado."
            )
        }

    return {}


# =====================================================
# CALCULAR HORA DE FINALIZACIÓN
# =====================================================

def calcular_hora_fin(fecha, hora_inicio, duracion):
    """Calcula la hora final según la duración del servicio."""

    try:
        duracion = int(duracion)

        if duracion <= 0:
            return None

        inicio = convertir_fecha_hora(
            fecha,
            hora_inicio
        )

        fin = inicio + timedelta(
            minutes=duracion
        )

        if fin.date() != inicio.date():
            return None

        return fin.strftime("%H:%M")

    except (ValueError, TypeError, OverflowError):
        return None


# =====================================================
# REGISTRAR CITA
# =====================================================

def registrar_cita(datos, id_establecimiento):

    # VALIDAR DATOS

    errores = validar_datos_cita(datos)

    if errores:
        return respuesta(
            False,
            "No fue posible registrar la cita.",
            errores=errores
        )

    id_cliente = int(datos["id_cliente"])
    id_servicio = int(datos["id_servicio"])

    fecha = datos["fecha"]
    hora_inicio = datos["hora_inicio"]

    # VALIDAR FECHA Y HORA FUTURA

    errores = validar_fecha_hora_futura(
        fecha,
        hora_inicio
    )

    if errores:
        return respuesta(
            False,
            "La fecha y hora seleccionadas no son válidas.",
            errores=errores
        )

    # VALIDAR CLIENTE DEL ESTABLECIMIENTO

    cliente = repositories.obtener_cliente_por_id(
        id_cliente,
        id_establecimiento
    )

    if not cliente:
        return respuesta(
            False,
            "El cliente no existe en este establecimiento."
        )

    # VALIDAR SERVICIO

    servicio = repositories.obtener_servicio_activo(
        id_servicio,
        id_establecimiento
    )

    if not servicio:
        return respuesta(
            False,
            "El servicio no existe o se encuentra inactivo."
        )

    # CALCULAR DURACIÓN

    duracion = servicio["duracion_minutos"]

    hora_fin = calcular_hora_fin(
        fecha,
        hora_inicio,
        duracion
    )

    if hora_fin is None:
        return respuesta(
            False,
            "No fue posible calcular la hora de finalización."
        )

    # VALIDAR DISPONIBILIDAD

    errores = validar_disponibilidad(
        id_establecimiento,
        fecha,
        hora_inicio,
        hora_fin
    )

    if errores:
        return respuesta(
            False,
            "El horario seleccionado no está disponible.",
            errores=errores
        )

    # REGISTRAR CITA

    id_cita = repositories.crear_cita(
        id_establecimiento,
        id_cliente,
        id_servicio,
        fecha,
        hora_inicio,
        hora_fin
    )

    if not id_cita:
        return respuesta(
            False,
            "No fue posible registrar la cita."
        )

    return respuesta(
        True,
        "Cita registrada correctamente.",
        {
            "id_cita": id_cita,
            "id_cliente": id_cliente,
            "id_servicio": id_servicio,
            "fecha": str(fecha),
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "duracion_minutos": duracion,
            "estado": "pendiente"
        }
    )


# =====================================================
# ACTUALIZAR CITA
# =====================================================

def actualizar_cita(
    id_cita,
    datos,
    id_establecimiento
):

    # VALIDAR DATOS

    errores = validar_datos_cita(datos)

    if errores:
        return respuesta(
            False,
            "No fue posible actualizar la cita.",
            errores=errores
        )

    # CONSULTAR CITA ACTUAL

    cita_actual = repositories.obtener_cita_por_id(
        id_cita,
        id_establecimiento
    )

    if not cita_actual:
        return respuesta(
            False,
            "No se encontró la cita solicitada."
        )

    if cita_actual["estado"] in (
        "cancelada",
        "completada"
    ):
        return respuesta(
            False,
            "No se pueden modificar citas canceladas o completadas."
        )

    id_cliente = int(datos["id_cliente"])
    id_servicio = int(datos["id_servicio"])

    fecha = datos["fecha"]
    hora_inicio = datos["hora_inicio"]

    # VALIDAR FECHA Y HORA FUTURA

    errores = validar_fecha_hora_futura(
        fecha,
        hora_inicio
    )

    if errores:
        return respuesta(
            False,
            "La fecha y hora seleccionadas no son válidas.",
            errores=errores
        )

    # VALIDAR CLIENTE DEL ESTABLECIMIENTO

    cliente = repositories.obtener_cliente_por_id(
        id_cliente,
        id_establecimiento
    )

    if not cliente:
        return respuesta(
            False,
            "El cliente no existe en este establecimiento."
        )

    # VALIDAR SERVICIO

    servicio = repositories.obtener_servicio_activo(
        id_servicio,
        id_establecimiento
    )

    if not servicio:
        return respuesta(
            False,
            "El servicio no existe o se encuentra inactivo."
        )

    # CALCULAR DURACIÓN

    duracion = servicio["duracion_minutos"]

    hora_fin = calcular_hora_fin(
        fecha,
        hora_inicio,
        duracion
    )

    if hora_fin is None:
        return respuesta(
            False,
            "No fue posible calcular la hora de finalización."
        )

    # VALIDAR DISPONIBILIDAD

    errores = validar_disponibilidad(
        id_establecimiento,
        fecha,
        hora_inicio,
        hora_fin,
        id_cita
    )

    if errores:
        return respuesta(
            False,
            "El horario seleccionado no está disponible.",
            errores=errores
        )

    # ACTUALIZAR CITA

    filas_afectadas = repositories.actualizar_cita(
        id_cita,
        id_establecimiento,
        id_cliente,
        id_servicio,
        fecha,
        hora_inicio,
        hora_fin
    )

    if filas_afectadas == 0:

        cita_verificacion = repositories.obtener_cita_por_id(
            id_cita,
            id_establecimiento
        )

        if not cita_verificacion:
            return respuesta(
                False,
                "No fue posible actualizar la cita."
            )

    return respuesta(
        True,
        "Cita actualizada correctamente.",
        {
            "id_cita": id_cita,
            "id_cliente": id_cliente,
            "id_servicio": id_servicio,
            "fecha": str(fecha),
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "duracion_minutos": duracion
        }
    )


# =====================================================
# CAMBIAR ESTADO DE UNA CITA
# =====================================================

def cambiar_estado_cita(
    id_cita,
    datos,
    id_establecimiento
):

    # VALIDAR ESTADO

    errores = validar_datos_estado(datos)

    if errores:
        return respuesta(
            False,
            "No fue posible cambiar el estado de la cita.",
            errores=errores
        )

    # CONSULTAR CITA

    cita = repositories.obtener_cita_por_id(
        id_cita,
        id_establecimiento
    )

    if not cita:
        return respuesta(
            False,
            "No se encontró la cita solicitada."
        )

    nuevo_estado = datos["estado"]
    estado_actual = cita["estado"]

    # VALIDAR TRANSICIONES

    if estado_actual == "cancelada":
        return respuesta(
            False,
            "No se puede modificar una cita cancelada."
        )

    if estado_actual == "completada":
        return respuesta(
            False,
            "No se puede modificar una cita completada."
        )

    if estado_actual == nuevo_estado:
        return respuesta(
            True,
            "La cita ya tiene ese estado.",
            serializar_cita(cita)
        )

    if (
        estado_actual == "pendiente"
        and nuevo_estado == "completada"
    ):
        return respuesta(
            False,
            "Primero debes confirmar la cita."
        )

    if (
        estado_actual == "confirmada"
        and nuevo_estado == "pendiente"
    ):
        return respuesta(
            False,
            "No se puede regresar una cita confirmada a pendiente."
        )

    # ACTUALIZAR ESTADO

    filas_afectadas = repositories.actualizar_estado_cita(
        id_cita,
        id_establecimiento,
        nuevo_estado
    )

    if filas_afectadas == 0:

        cita_verificacion = repositories.obtener_cita_por_id(
            id_cita,
            id_establecimiento
        )

        if not cita_verificacion:
            return respuesta(
                False,
                "No fue posible actualizar el estado de la cita."
            )

        if cita_verificacion["estado"] != nuevo_estado:
            return respuesta(
                False,
                "No fue posible actualizar el estado de la cita."
            )

    # NOTIFICAR AL CLIENTE CUANDO SE CONFIRMA LA CITA

    if (
        estado_actual == "pendiente"
        and nuevo_estado == "confirmada"
    ):
        notificar_confirmacion_whatsapp(cita)

    return respuesta(
        True,
        "Estado de la cita actualizado correctamente.",
        
        {
            "id_cita": id_cita,
            "estado": nuevo_estado
        }
    )


# =====================================================
# LISTAR CLIENTES
# =====================================================

def listar_clientes(id_establecimiento):
    """Obtiene únicamente los clientes del establecimiento."""

    try:
        clientes = repositories.obtener_todos_los_clientes(
            id_establecimiento
        )

        return respuesta(
            True,
            "Clientes consultados correctamente.",
            data=clientes
        )

    except Exception as error:
        print("Error al listar clientes:", error)

        return respuesta(
            False,
            "No fue posible consultar los clientes."
        )


# =====================================================
# NOTIFICAR CONFIRMACIÓN DE CITA POR WHATSAPP
# =====================================================

def notificar_confirmacion_whatsapp(cita):
    """Envía al cliente la confirmación de su cita."""

    try:
        from apps.establishment import repositories as establishment_repository
        from apps.whatsapp.services import enviar_mensaje_whatsapp

        id_cita = cita["id_cita"]

        # REGISTRAR NOTIFICACIÓN Y EVITAR DUPLICADOS
        registrada = repositories.registrar_notificacion_confirmacion_whatsapp(
            id_cita
        )

        if not registrada:
            return

        # OBTENER DATOS DEL ESTABLECIMIENTO
        establecimiento = establishment_repository.obtener_establecimiento_por_id(
            cita["id_establecimiento"]
        )

        if not establecimiento:
            raise ValueError("No se encontró el establecimiento.")

        phone_number_id = establecimiento.get(
            "whatsapp_phone_number_id"
        )

        telefono = cita.get("telefono_cliente")

        if not telefono or not phone_number_id:
            raise ValueError("Faltan datos para enviar la notificación.")

        fecha = cita["fecha"]
        hora = cita["hora_inicio"]

        if hasattr(fecha, "strftime"):
            fecha = fecha.strftime("%d/%m/%Y")

        if hasattr(hora, "strftime"):
            hora = hora.strftime("%H:%M")

        mensaje = (
            f"¡Hola, {cita['nombre_cliente']}! "
            "Tu cita ha sido confirmada.\n\n"
            f"Servicio: {cita['nombre_servicio']}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Establecimiento: {establecimiento['nombre_comercial']}\n"
            "¡Te esperamos!"
        )

        # ENVIAR MENSAJE
        resultado = enviar_mensaje_whatsapp(
            telefono,
            mensaje,
            phone_number_id
        )

        if resultado.get("ok"):
            estado = "enviada"
            detalle = "Mensaje aceptado por WhatsApp."
        else:
            estado = "fallida"
            detalle = resultado.get("error", "Error desconocido.")

        repositories.actualizar_notificacion_whatsapp(
            id_cita,
            estado,
            detalle
        )

    except Exception as error:
        print(
            f"Error al notificar confirmación de cita "
            f"{cita.get('id_cita')}: {error}"
        )

        try:
            repositories.actualizar_notificacion_whatsapp(
                cita["id_cita"],
                "fallida",
                "No fue posible procesar el envío."
            )
        except Exception:
            print("No fue posible actualizar el registro de notificación.")


# =====================================================
# CONSULTAR HORARIOS DISPONIBLES
# =====================================================

def consultar_horarios_disponibles(
    id_establecimiento,
    id_servicio,
    fecha
):
    """Genera los horarios disponibles según la duración del servicio."""

    try:
        # VALIDAR SERVICIO

        servicio = repositories.obtener_servicio_activo(
            id_servicio,
            id_establecimiento
        )

        if not servicio:
            return respuesta(
                False,
                "El servicio no existe o está inactivo."
            )

        duracion = int(servicio["duracion_minutos"])

        if duracion <= 0:
            return respuesta(
                False,
                "La duración del servicio no es válida."
            )

        # VALIDAR FECHA

        if isinstance(fecha, datetime):
            fecha_obj = fecha.date()
        elif isinstance(fecha, date):
            fecha_obj = fecha
        else:
            fecha_obj = datetime.strptime(
                str(fecha),
                "%Y-%m-%d"
            ).date()

        if fecha_obj < date.today():
            return respuesta(
                False,
                "No se pueden consultar fechas pasadas."
            )

        fecha = fecha_obj.strftime("%Y-%m-%d")

        # CONSULTAR HORARIO DEL ESTABLECIMIENTO

        dia = obtener_dia_semana(fecha)

        horario = repositories.obtener_horario_por_dia(
            id_establecimiento,
            dia
        )

        if not horario:
            return respuesta(
                False,
                "El establecimiento no atiende ese día."
            )

        inicio = convertir_fecha_hora(
            fecha,
            horario["hora_inicio"]
        )

        fin = convertir_fecha_hora(
            fecha,
            horario["hora_fin"]
        )

        # GENERAR HORARIOS

        horarios = []
        actual = inicio

        while actual + timedelta(minutes=duracion) <= fin:

            hora_inicio = actual.strftime("%H:%M")
            
            if validar_fecha_hora_futura(fecha, hora_inicio):
                actual += timedelta(minutes=duracion)
                continue

            hora_fin = calcular_hora_fin(
                fecha,
                hora_inicio,
                duracion
            )

            if hora_fin:

                errores = validar_disponibilidad(
                    id_establecimiento,
                    fecha,
                    hora_inicio,
                    hora_fin
                )

                if not errores:

                    horarios.append({
                        "hora_inicio": hora_inicio,
                        "hora_fin": hora_fin
                    })

            actual += timedelta(minutes=duracion)

        return respuesta(
            True,
            "Horarios disponibles consultados correctamente.",
            {
                "fecha": fecha,
                "id_servicio": id_servicio,
                "duracion_minutos": duracion,
                "horarios": horarios
            }
        )

    except Exception as error:
        print("Error al consultar horarios disponibles:", error)

        return respuesta(
            False,
            "No fue posible consultar los horarios disponibles."
        )
        



# =====================================================
# CREAR CITA DESDE LA CUENTA DEL CLIENTE
# =====================================================

def crear_cita_usuario(id_usuario, datos):
    """Registra una cita solicitada por un cliente autenticado."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Los datos enviados no tienen un formato válido."
        )

    id_establecimiento = datos.get("id_establecimiento")
    id_servicio = datos.get("id_servicio")
    fecha = datos.get("fecha")
    hora_inicio = datos.get("hora_inicio")

    # VALIDAR IDENTIFICADORES

    errores = {}

    if not validar_identificador(id_establecimiento):
        errores["id_establecimiento"] = (
            "Debes seleccionar un establecimiento válido."
        )

    if not validar_identificador(id_servicio):
        errores["id_servicio"] = (
            "Debes seleccionar un servicio válido."
        )

    # VALIDAR FECHA Y HORA

    if not validar_fecha(fecha):
        errores["fecha"] = (
            "La fecha debe ser válida y no puede ser anterior al día actual."
        )

    if not validar_hora(hora_inicio):
        errores["hora_inicio"] = (
            "La hora de inicio debe tener el formato HH:MM."
        )

    if errores:
        return respuesta(
            False,
            "Verifica los datos de la reserva.",
            errores=errores
        )

    # VALIDAR QUE LA FECHA Y HORA SEAN FUTURAS

    errores = validar_fecha_hora_futura(
        fecha,
        hora_inicio
    )

    if errores:
        return respuesta(
            False,
            "La fecha y hora seleccionadas no son válidas.",
            errores=errores
        )

    try:
        # CONSULTAR SERVICIO ACTIVO

        servicio = repositories.obtener_servicio_activo(
            id_servicio,
            id_establecimiento
        )

        if not servicio:
            return respuesta(
                False,
                "El servicio no existe o está inactivo."
            )

        duracion = servicio.get("duracion_minutos")

        if not duracion or int(duracion) <= 0:
            return respuesta(
                False,
                "La duración del servicio no es válida."
            )

        # CALCULAR HORA DE FINALIZACIÓN

        hora_fin = calcular_hora_fin(
            fecha,
            hora_inicio,
            duracion
        )

        if hora_fin is None:
            return respuesta(
                False,
                "No fue posible calcular la hora de finalización."
            )

        # OBTENER DÍA DE LA SEMANA

        dia = obtener_dia_semana(fecha)

        # REGISTRAR CITA

        resultado = repositories.crear_cita_usuario(
            id_usuario,
            id_establecimiento,
            id_servicio,
            fecha,
            dia,
            hora_inicio,
            hora_fin
        )

        if not resultado.get("ok"):
            return respuesta(
                False,
                resultado.get(
                    "mensaje",
                    "No fue posible reservar la cita."
                )
            )

        return respuesta(
            True,
            resultado.get(
                "mensaje",
                "La cita fue reservada correctamente."
            ),
            {
                "id_cita": resultado.get("id_cita"),
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin
            }
        )

    except Exception as error:
        print("Error al crear cita de usuario:", error)

        return respuesta(
            False,
            "Ocurrió un error al intentar reservar la cita."
        )
