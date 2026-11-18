
from datetime import datetime


# =====================================================
# DÍAS DE LA SEMANA
# =====================================================

DIAS_SEMANA = (
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "viernes",
    "sabado",
    "domingo"
)


# =====================================================
# VALIDAR DÍA
# =====================================================

def validar_dia(dia):
    """Comprueba que el día sea válido."""

    if not isinstance(dia, str):
        return False

    return dia.strip().lower() in DIAS_SEMANA


# =====================================================
# VALIDAR HORA
# =====================================================

def validar_hora(hora):
    """Comprueba que la hora tenga formato HH:MM."""

    if not isinstance(hora, str):
        return False

    try:
        datetime.strptime(hora, "%H:%M")
        return True

    except ValueError:
        return False


# =====================================================
# VALIDAR ESTADO
# =====================================================

def validar_estado(estado):
    """Comprueba que el estado sea 0 o 1."""

    if isinstance(estado, bool):
        return False

    return estado in (0, 1)



# =====================================================
# VALIDAR DATOS DEL ESTADO
# =====================================================

def validar_datos_estado(datos):
    """Valida los datos enviados para cambiar el estado."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "general": "Los datos del estado no son válidos."
        }

    estado = datos.get("estado")

    if not validar_estado(estado):
        errores["estado"] = "El estado debe ser 0 o 1."

    return errores


# =====================================================
# VALIDAR DATOS DEL HORARIO
# =====================================================


def validar_datos_horario(datos):
    """Valida los datos de un horario y su descanso opcional."""

    errores = {}

    if not isinstance(datos, dict):
        return {"general": "Los datos deben tener un formato válido."}

    dia = datos.get("dia")
    hora_inicio = datos.get("hora_inicio")
    hora_fin = datos.get("hora_fin")

    hora_inicio_descanso = datos.get("hora_inicio_descanso")
    hora_fin_descanso = datos.get("hora_fin_descanso")

    # VALIDAR DÍA

    if not validar_dia(dia):
        errores["dia"] = "El día seleccionado no es válido."

    # VALIDAR HORAS DE ATENCIÓN

    if not validar_hora(hora_inicio):
        errores["hora_inicio"] = "La hora de inicio no es válida."

    if not validar_hora(hora_fin):
        errores["hora_fin"] = "La hora de cierre no es válida."

    if (
        validar_hora(hora_inicio)
        and validar_hora(hora_fin)
    ):
        inicio = datetime.strptime(hora_inicio, "%H:%M")
        fin = datetime.strptime(hora_fin, "%H:%M")

        if inicio >= fin:
            errores["hora_fin"] = (
                "La hora de cierre debe ser posterior a la hora de inicio."
            )

    # VALIDAR DESCANSO OPCIONAL

    if hora_inicio_descanso is None and hora_fin_descanso is None:
        return errores

    if hora_inicio_descanso is None or hora_fin_descanso is None:
        errores["descanso"] = (
            "Debes indicar ambas horas del descanso."
        )
        return errores

    if not validar_hora(hora_inicio_descanso):
        errores["hora_inicio_descanso"] = (
            "La hora de inicio del descanso no es válida."
        )

    if not validar_hora(hora_fin_descanso):
        errores["hora_fin_descanso"] = (
            "La hora de finalización del descanso no es válida."
        )

    # VALIDAR ORDEN Y LÍMITES DEL DESCANSO

    if (
        validar_hora(hora_inicio)
        and validar_hora(hora_fin)
        and validar_hora(hora_inicio_descanso)
        and validar_hora(hora_fin_descanso)
    ):
        inicio = datetime.strptime(hora_inicio, "%H:%M")
        fin = datetime.strptime(hora_fin, "%H:%M")

        inicio_descanso = datetime.strptime(
            hora_inicio_descanso, "%H:%M"
        )

        fin_descanso = datetime.strptime(
            hora_fin_descanso, "%H:%M"
        )

        if inicio_descanso >= fin_descanso:
            errores["hora_fin_descanso"] = (
                "El fin del descanso debe ser posterior a su inicio."
            )

        if inicio_descanso <= inicio:
            errores["hora_inicio_descanso"] = (
                "El descanso debe comenzar después de abrir."
            )

        if fin_descanso >= fin:
            errores["hora_fin_descanso"] = (
                "El descanso debe terminar antes del cierre."
            )

    return errores



# =====================================================
# NORMALIZAR DATOS
# =====================================================

def normalizar_horario(datos):
    """Normaliza los datos antes de guardarlos."""

    return {
        "dia": datos.get("dia").strip().lower(),
        "hora_inicio": datos.get("hora_inicio"),
        "hora_fin": datos.get("hora_fin"),
        "hora_inicio_descanso": (
            datos.get("hora_inicio_descanso") or None
        ),
        "hora_fin_descanso": (
            datos.get("hora_fin_descanso") or None
        )
    }


# =====================================================
# NORMALIZAR HORA PARA RESPUESTAS
# =====================================================

def serializar_hora(valor):
    """Convierte una hora a formato HH:MM."""

    if valor is None:
        return None

    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")

    valor = str(valor).strip()

    try:
        return datetime.strptime(
            valor[:8], "%H:%M:%S"
        ).strftime("%H:%M")

    except ValueError:
        try:
            return datetime.strptime(
                valor, "%H:%M"
            ).strftime("%H:%M")

        except ValueError:
            return None


# =====================================================
# SERIALIZAR HORARIO
# =====================================================

def serializar_horario(horario):
    """Convierte un horario de la base de datos a diccionario."""

    if not horario:
        return None

    return {
        "id_horario": horario.get("id_horario"),
        "id_establecimiento": horario.get("id_establecimiento"),
        "dia": horario.get("dia"),
        "hora_inicio": serializar_hora(
            horario.get("hora_inicio")
        ),
        "hora_fin": serializar_hora(
            horario.get("hora_fin")
        ),
        "hora_inicio_descanso": serializar_hora(
            horario.get("hora_inicio_descanso")
        ),
        "hora_fin_descanso": serializar_hora(
            horario.get("hora_fin_descanso")
        ),
        "estado": horario.get("estado")
    }


# =====================================================
# SERIALIZAR LISTA DE HORARIOS
# =====================================================

def serializar_horarios(horarios):
    """Convierte una lista de horarios a diccionarios."""

    return [
        serializar_horario(horario)
        for horario in horarios
    ]


# =====================================================
# SERIALIZAR HORARIOS DISPONIBLES PARA CLIENTES
# =====================================================

def serializar_horarios_disponibles(horarios):
    """Serializa los horarios activos sin datos administrativos."""

    return [
        {
            "id_horario": horario.get("id_horario"),
            "id_establecimiento": horario.get("id_establecimiento"),
            "dia": horario.get("dia"),
            "hora_inicio": serializar_hora(
                horario.get("hora_inicio")
            ),
            "hora_fin": serializar_hora(
                horario.get("hora_fin")
            ),
            "hora_inicio_descanso": serializar_hora(
                horario.get("hora_inicio_descanso")
            ),
            "hora_fin_descanso": serializar_hora(
                horario.get("hora_fin_descanso")
            )
        }
        for horario in horarios
    ]