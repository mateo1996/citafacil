
from decimal import Decimal, InvalidOperation

from apps.services import repositories
from apps.services import serializers


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
    """Normaliza los datos recibidos para un servicio."""

    datos = datos.copy()

    if isinstance(datos.get("nombre"), str):
        datos["nombre"] = datos["nombre"].strip()

    if isinstance(datos.get("descripcion"), str):
        datos["descripcion"] = datos["descripcion"].strip() or None

    return datos


# =====================================================
# CONVERTIR PRECIO
# =====================================================

def convertir_precio(precio):
    """Convierte el precio a Decimal para su almacenamiento."""

    if isinstance(precio, bool):
        raise ValueError("El precio no es válido.")

    try:
        valor = Decimal(str(precio))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El precio no es válido.")

    if not valor.is_finite():
        raise ValueError("El precio no es válido.")

    return valor


# =====================================================
# LISTAR SERVICIOS
# =====================================================

def obtener_servicios(id_establecimiento):
    """Obtiene todos los servicios de un establecimiento."""

    servicios = repositories.obtener_servicios_por_establecimiento(
        id_establecimiento
    )

    servicios_serializados = serializers.serializar_servicios(
        servicios
    )

    return respuesta(
        True,
        "Servicios consultados correctamente.",
        servicios_serializados
    )


# =====================================================
# OBTENER SERVICIO POR ID
# =====================================================

def obtener_servicio(id_servicio, id_establecimiento):
    """Obtiene un servicio perteneciente al establecimiento."""

    servicio = repositories.obtener_servicio_por_id(
        id_servicio,
        id_establecimiento
    )

    if not servicio:
        return respuesta(
            False,
            "El servicio no existe o no pertenece a este establecimiento."
        )

    return respuesta(
        True,
        "Servicio consultado correctamente.",
        serializers.serializar_servicio(servicio)
    )


# =====================================================
# REGISTRAR SERVICIO
# =====================================================

def registrar_servicio(id_establecimiento, datos):
    """Registra un nuevo servicio para el establecimiento."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Debes enviar datos válidos.",
            errores={
                "general": "Los datos del servicio no son válidos."
            }
        )

    datos = normalizar_datos(datos)

    errores = serializers.validar_datos_servicio(datos)

    if errores:
        return respuesta(
            False,
            "Revisa los datos del servicio.",
            errores=errores
        )

    try:
        precio = convertir_precio(datos["precio"])

        id_servicio = repositories.crear_servicio(
            id_establecimiento=id_establecimiento,
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            duracion_minutos=datos["duracion_minutos"],
            precio=precio
        )

        servicio = repositories.obtener_servicio_por_id(
            id_servicio,
            id_establecimiento
        )

        return respuesta(
            True,
            "Servicio registrado correctamente.",
            serializers.serializar_servicio(servicio)
        )

    except Exception:
        raise


# =====================================================
# ACTUALIZAR SERVICIO
# =====================================================

def actualizar_servicio(id_servicio, id_establecimiento, datos):
    """Actualiza los datos de un servicio."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Debes enviar datos válidos.",
            errores={
                "general": "Los datos del servicio no son válidos."
            }
        )

    servicio_actual = repositories.obtener_servicio_por_id(
        id_servicio,
        id_establecimiento
    )

    if not servicio_actual:
        return respuesta(
            False,
            "El servicio no existe o no pertenece a este establecimiento."
        )

    datos = normalizar_datos(datos)

    errores = serializers.validar_datos_servicio(datos)

    if errores:
        return respuesta(
            False,
            "Revisa los datos del servicio.",
            errores=errores
        )

    try:
        precio = convertir_precio(datos["precio"])

        repositories.actualizar_servicio(
            id_servicio=id_servicio,
            id_establecimiento=id_establecimiento,
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            duracion_minutos=datos["duracion_minutos"],
            precio=precio
        )

        servicio_actualizado = repositories.obtener_servicio_por_id(
            id_servicio,
            id_establecimiento
        )

        return respuesta(
            True,
            "Servicio actualizado correctamente.",
            serializers.serializar_servicio(servicio_actualizado)
        )

    except Exception:
        raise


# =====================================================
# ACTIVAR O DESACTIVAR SERVICIO
# =====================================================

def cambiar_estado_servicio(
    id_servicio,
    id_establecimiento,
    estado
):
    """Activa o desactiva un servicio."""

    if isinstance(estado, bool):
        estado = int(estado)

    if estado not in (0, 1):
        return respuesta(
            False,
            "El estado debe ser 1 (activo) o 0 (inactivo).",
            errores={
                "estado": "El estado enviado no es válido."
            }
        )

    servicio = repositories.obtener_servicio_por_id(
        id_servicio,
        id_establecimiento
    )

    if not servicio:
        return respuesta(
            False,
            "El servicio no existe o no pertenece a este establecimiento."
        )

    try:
        repositories.actualizar_estado_servicio(
            id_servicio,
            id_establecimiento,
            estado
        )

        servicio_actualizado = repositories.obtener_servicio_por_id(
            id_servicio,
            id_establecimiento
        )

        mensaje = (
            "Servicio activado correctamente."
            if estado == 1
            else "Servicio desactivado correctamente."
        )

        return respuesta(
            True,
            mensaje,
            serializers.serializar_servicio(servicio_actualizado)
        )

    except Exception:
        raise



# =====================================================
# LISTAR SERVICIOS ACTIVOS PARA CLIENTES
# =====================================================

def obtener_servicios_activos(id_establecimiento):
    """Obtiene los servicios activos de un establecimiento."""

    servicios = (
        repositories.obtener_servicios_activos_por_establecimiento(
            id_establecimiento
        )
    )

    servicios_serializados = serializers.serializar_servicios_disponibles(
        servicios
    )

    return respuesta(
        True,
        "Servicios disponibles consultados correctamente.",
        servicios_serializados
    )
