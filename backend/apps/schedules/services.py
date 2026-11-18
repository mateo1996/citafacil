
from apps.schedules import repositories
from apps.schedules import serializers


# =====================================================
# RESPUESTA ESTÁNDAR
# =====================================================

def respuesta(ok, mensaje, data=None, errores=None):
    """Construye una respuesta estándar del servicio."""

    return {
        "ok": ok,
        "mensaje": mensaje,
        "data": data,
        "errores": errores or {}
    }


# =====================================================
# NORMALIZAR DATOS
# =====================================================

def normalizar_datos(datos):
    """Normaliza los datos recibidos para un horario."""

    datos = datos.copy()

    if isinstance(datos.get("dia"), str):
        datos["dia"] = datos["dia"].strip().lower()

    for campo in (
        "hora_inicio",
        "hora_fin",
        "hora_inicio_descanso",
        "hora_fin_descanso"
    ):
        if isinstance(datos.get(campo), str):
            datos[campo] = datos[campo].strip() or None

    return datos


# =====================================================
# LISTAR HORARIOS
# =====================================================

def obtener_horarios(id_establecimiento):
    """Obtiene todos los horarios de un establecimiento."""

    horarios = repositories.obtener_horarios_por_establecimiento(
        id_establecimiento
    )

    horarios_serializados = serializers.serializar_horarios(
        horarios
    )

    return respuesta(
        True,
        "Horarios consultados correctamente.",
        horarios_serializados
    )


# =====================================================
# OBTENER HORARIO POR ID
# =====================================================

def obtener_horario(id_horario, id_establecimiento):
    """Obtiene un horario perteneciente al establecimiento."""

    horario = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    if not horario:
        return respuesta(
            False,
            "El horario no existe o no pertenece a este establecimiento."
        )

    return respuesta(
        True,
        "Horario consultado correctamente.",
        serializers.serializar_horario(horario)
    )


# =====================================================
# REGISTRAR HORARIO
# =====================================================

def registrar_horario(id_establecimiento, datos):
    """Registra el horario de un día para el establecimiento."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Debes enviar datos válidos.",
            errores={
                "general": "Los datos del horario no son válidos."
            }
        )

    datos = normalizar_datos(datos)

    errores = serializers.validar_datos_horario(datos)

    if errores:
        return respuesta(
            False,
            "Revisa los datos del horario.",
            errores=errores
        )

    # COMPROBAR SI YA EXISTE UN HORARIO PARA EL DÍA

    horario_existente = repositories.obtener_horario_por_dia(
        id_establecimiento,
        datos["dia"]
    )

    if horario_existente:
        return respuesta(
            False,
            "Ya existe un horario configurado para este día.",
            errores={
                "dia": "Este día ya tiene un horario registrado."
            }
        )

    horario_normalizado = serializers.normalizar_horario(datos)

    id_horario = repositories.crear_horario(
        id_establecimiento=id_establecimiento,
        dia=horario_normalizado["dia"],
        hora_inicio=horario_normalizado["hora_inicio"],
        hora_fin=horario_normalizado["hora_fin"],
        hora_inicio_descanso=horario_normalizado[
            "hora_inicio_descanso"
        ],
        hora_fin_descanso=horario_normalizado[
            "hora_fin_descanso"
        ]
    )

    horario = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    return respuesta(
        True,
        "Horario registrado correctamente.",
        serializers.serializar_horario(horario)
    )


# =====================================================
# ACTUALIZAR HORARIO
# =====================================================

def actualizar_horario(
    id_horario,
    id_establecimiento,
    datos
):
    """Actualiza el horario de un día."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Debes enviar datos válidos.",
            errores={
                "general": "Los datos del horario no son válidos."
            }
        )

    horario_actual = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    if not horario_actual:
        return respuesta(
            False,
            "El horario no existe o no pertenece a este establecimiento."
        )

    datos = normalizar_datos(datos)

    errores = serializers.validar_datos_horario(datos)

    if errores:
        return respuesta(
            False,
            "Revisa los datos del horario.",
            errores=errores
        )

    # COMPROBAR SI EL NUEVO DÍA YA TIENE OTRO HORARIO

    horario_existente = repositories.obtener_horario_por_dia(
        id_establecimiento,
        datos["dia"]
    )

    if (
        horario_existente
        and horario_existente["id_horario"] != id_horario
    ):
        return respuesta(
            False,
            "Ya existe un horario configurado para este día.",
            errores={
                "dia": "Este día ya tiene un horario registrado."
            }
        )

    horario_normalizado = serializers.normalizar_horario(datos)

    repositories.actualizar_horario(
        id_horario=id_horario,
        id_establecimiento=id_establecimiento,
        dia=horario_normalizado["dia"],
        hora_inicio=horario_normalizado["hora_inicio"],
        hora_fin=horario_normalizado["hora_fin"],
        hora_inicio_descanso=horario_normalizado[
            "hora_inicio_descanso"
        ],
        hora_fin_descanso=horario_normalizado[
            "hora_fin_descanso"
        ]
    )

    horario_actualizado = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    return respuesta(
        True,
        "Horario actualizado correctamente.",
        serializers.serializar_horario(horario_actualizado)
    )


# =====================================================
# ACTIVAR O DESACTIVAR HORARIO
# =====================================================

def cambiar_estado_horario(
    id_horario,
    id_establecimiento,
    estado
):
    """Activa o desactiva el horario de un día."""

    errores = serializers.validar_datos_estado({
        "estado": estado
    })

    if errores:
        return respuesta(
            False,
            "El estado enviado no es válido.",
            errores=errores
        )

    horario = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    if not horario:
        return respuesta(
            False,
            "El horario no existe o no pertenece a este establecimiento."
        )

    repositories.actualizar_estado_horario(
        id_horario,
        id_establecimiento,
        estado
    )

    horario_actualizado = repositories.obtener_horario_por_id(
        id_horario,
        id_establecimiento
    )

    mensaje = (
        "Horario activado correctamente."
        if estado == 1
        else "Horario desactivado correctamente."
    )

    return respuesta(
        True,
        mensaje,
        serializers.serializar_horario(horario_actualizado)
    )


# =====================================================
# LISTAR HORARIOS ACTIVOS PARA CLIENTES
# =====================================================

def obtener_horarios_activos(id_establecimiento):
    """Obtiene únicamente los horarios activos de un establecimiento."""

    horarios = (
        repositories.obtener_horarios_activos_por_establecimiento(
            id_establecimiento
        )
    )

    horarios_serializados = serializers.serializar_horarios_disponibles(
        horarios
    )

    return respuesta(
        True,
        "Horarios disponibles consultados correctamente.",
        horarios_serializados
    )
    

