
from datetime import date, datetime, time


# =====================================================
# ESTADOS PERMITIDOS
# =====================================================

ESTADOS_CITA = (
    "pendiente",
    "confirmada",
    "cancelada",
    "completada"
)


# =====================================================
# VALIDAR IDENTIFICADOR
# =====================================================

def validar_identificador(valor):
    """Comprueba que un identificador sea un entero positivo."""

    if isinstance(valor, bool):
        return False

    try:
        numero = int(valor)
    except (ValueError, TypeError):
        return False

    return numero > 0 and str(numero) == str(valor).strip()


# =====================================================
# VALIDAR FECHA
# =====================================================

def validar_fecha(valor):
    """Comprueba que la fecha tenga formato YYYY-MM-DD y sea válida."""

    if isinstance(valor, datetime):
        fecha = valor.date()

    elif isinstance(valor, date):
        fecha = valor

    elif isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            return False

    else:
        return False

    return fecha >= date.today()


# =====================================================
# VALIDAR HORA
# =====================================================

def validar_hora(valor):
    """Comprueba que la hora tenga formato HH:MM."""

    if isinstance(valor, time):
        return True

    if not isinstance(valor, str):
        return False

    try:
        datetime.strptime(valor, "%H:%M")
        return True

    except ValueError:
        return False


# =====================================================
# CONVERTIR HORA A TIME
# =====================================================

def convertir_hora(valor):
    """Convierte una hora HH:MM o un objeto time a datetime.time."""

    if isinstance(valor, time):
        return valor

    if not validar_hora(valor):
        raise ValueError("La hora debe tener el formato HH:MM.")

    return datetime.strptime(valor, "%H:%M").time()


# =====================================================
# VALIDAR INTERVALO DE HORAS
# =====================================================

def validar_intervalo_horas(hora_inicio, hora_fin):
    """Comprueba que la hora de inicio sea anterior a la finalización."""

    try:
        inicio = convertir_hora(hora_inicio)
        fin = convertir_hora(hora_fin)

        return inicio < fin

    except (ValueError, TypeError):
        return False



# =====================================================
# VALIDAR DATOS DE UNA CITA
# =====================================================

def validar_datos_cita(datos):
    """Valida los datos necesarios para registrar o actualizar una cita."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos enviados no tienen un formato válido."
        }

    # -------------------------------------------------
    # CLIENTE
    # -------------------------------------------------

    id_cliente = datos.get("id_cliente")

    if not validar_identificador(id_cliente):
        errores["id_cliente"] = (
            "Debes seleccionar un cliente válido."
        )

    # -------------------------------------------------
    # SERVICIO
    # -------------------------------------------------

    id_servicio = datos.get("id_servicio")

    if not validar_identificador(id_servicio):
        errores["id_servicio"] = (
            "Debes seleccionar un servicio válido."
        )

    # -------------------------------------------------
    # FECHA
    # -------------------------------------------------

    fecha = datos.get("fecha")

    if not validar_fecha(fecha):
        errores["fecha"] = (
            "La fecha debe ser válida y no puede ser anterior al día actual."
        )

    # -------------------------------------------------
    # HORA DE INICIO
    # -------------------------------------------------

    hora_inicio = datos.get("hora_inicio")

    if not validar_hora(hora_inicio):
        errores["hora_inicio"] = (
            "La hora de inicio debe tener el formato HH:MM."
        )

    return errores


# =====================================================
# VALIDAR DATOS DEL ESTADO
# =====================================================

def validar_datos_estado(datos):
    """Valida el estado que se asignará a una cita."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos enviados no tienen un formato válido."
        }

    estado = datos.get("estado")

    if not isinstance(estado, str):
        errores["estado"] = "El estado debe ser un texto válido."

    elif estado not in ESTADOS_CITA:
        errores["estado"] = (
            "El estado debe ser pendiente, confirmada, cancelada o completada."
        )

    return errores


# =====================================================
# SERIALIZAR CITA
# =====================================================


def serializar_cita(cita):
    """Convierte una cita obtenida de MySQL en un diccionario serializable."""

    if not cita:
        return None

    resultado = dict(cita)

    # -------------------------------------------------
    # FECHAS
    # -------------------------------------------------

    for campo in ("fecha", "fecha_creacion"):
        valor = resultado.get(campo)

        if isinstance(valor, (date, datetime)):
            resultado[campo] = valor.isoformat()

    # -------------------------------------------------
    # HORAS
    # -------------------------------------------------

    for campo in ("hora_inicio", "hora_fin"):
        valor = resultado.get(campo)

        if isinstance(valor, (time, datetime)):
            resultado[campo] = valor.strftime("%H:%M")

        elif valor is not None:
            texto = str(valor)

            try:
                resultado[campo] = datetime.strptime(
                    texto,
                    "%H:%M:%S"
                ).strftime("%H:%M")

            except ValueError:
                try:
                    resultado[campo] = datetime.strptime(
                        texto,
                        "%H:%M"
                    ).strftime("%H:%M")

                except ValueError:
                    resultado[campo] = texto

    # -------------------------------------------------
    # PRECIO
    # -------------------------------------------------

    if resultado.get("precio") is not None:
        resultado["precio"] = float(resultado["precio"])

    return resultado



# =====================================================
# SERIALIZAR LISTA DE CITAS
# =====================================================

def serializar_citas(citas):
    """Serializa una lista de citas."""

    return [
        serializar_cita(cita)
        for cita in citas
    ]


# =====================================================
# SERIALIZAR CITAS DEL CLIENTE
# =====================================================

def serializar_citas_usuario(citas):
    """Serializa las citas visibles para el cliente."""

    campos_permitidos = (
        "id_cita",
        "fecha",
        "hora_inicio",
        "hora_fin",
        "estado",
        "nombre_establecimiento",
        "direccion_establecimiento",
        "nombre_servicio",
        "duracion_minutos",
        "precio"
    )

    resultado = []

    for cita in citas:
        cita_serializada = serializar_cita(cita)

        resultado.append({
            campo: cita_serializada.get(campo)
            for campo in campos_permitidos
        })

    return resultado