
from decimal import Decimal, InvalidOperation


# =====================================================
# VALIDAR NOMBRE DEL SERVICIO
# =====================================================

def validar_nombre_servicio(nombre):
    """Comprueba que el nombre del servicio sea válido."""

    if not isinstance(nombre, str):
        return False

    nombre = nombre.strip()

    return 2 <= len(nombre) <= 100


# =====================================================
# VALIDAR DESCRIPCIÓN
# =====================================================

def validar_descripcion(descripcion):
    """Comprueba que la descripción sea válida."""

    if descripcion is None or descripcion == "":
        return True

    if not isinstance(descripcion, str):
        return False

    return len(descripcion.strip()) <= 5000


# =====================================================
# VALIDAR DURACIÓN
# =====================================================

def validar_duracion(duracion):
    """Comprueba que la duración sea un entero positivo."""

    if isinstance(duracion, bool):
        return False

    try:
        valor = int(duracion)
    except (ValueError, TypeError, OverflowError):
        return False

    if isinstance(duracion, float) and not duracion.is_integer():
        return False

    if isinstance(duracion, str) and str(valor) != duracion.strip():
        return False

    return valor > 0


# =====================================================
# VALIDAR PRECIO
# =====================================================

def validar_precio(precio):
    """Comprueba que el precio sea válido para DECIMAL(10,2)."""

    if isinstance(precio, bool):
        return False

    try:
        valor = Decimal(str(precio))
    except (InvalidOperation, ValueError, TypeError):
        return False

    if not valor.is_finite() or valor < 0:
        return False

    if valor.as_tuple().exponent < -2:
        return False

    return valor <= Decimal("99999999.99")


# =====================================================
# VALIDAR ESTADO
# =====================================================

def validar_estado(estado):
    """Comprueba que el estado sea 1 (activo) o 0 (inactivo)."""

    if isinstance(estado, bool):
        return False

    return estado in (0, 1)


# =====================================================
# VALIDAR DATOS DEL SERVICIO
# =====================================================

def validar_datos_servicio(datos):
    """Valida los datos necesarios para registrar o actualizar un servicio."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "general": "Los datos del servicio no son válidos."
        }

    nombre = datos.get("nombre")
    descripcion = datos.get("descripcion")
    duracion = datos.get("duracion_minutos")
    precio = datos.get("precio", 0)

    # NOMBRE
    if not validar_nombre_servicio(nombre):
        errores["nombre"] = (
            "El nombre debe tener entre 2 y 100 caracteres."
        )

    # DESCRIPCIÓN
    if not validar_descripcion(descripcion):
        errores["descripcion"] = (
            "La descripción no puede superar los 5000 caracteres."
        )

    # DURACIÓN
    if not validar_duracion(duracion):
        errores["duracion_minutos"] = (
            "La duración debe ser un número entero mayor que cero."
        )

    # PRECIO
    if not validar_precio(precio):
        errores["precio"] = (
            "El precio debe ser un número válido, "
            "mayor o igual a cero y con máximo dos decimales."
        )

    return errores


# =====================================================
# VALIDAR CAMBIO DE ESTADO
# =====================================================

def validar_datos_estado(datos):
    """Valida los datos para activar o desactivar un servicio."""

    if not isinstance(datos, dict):
        return {
            "general": "Los datos enviados no son válidos."
        }

    estado = datos.get("estado")

    if not validar_estado(estado):
        return {
            "estado": "El estado debe ser 1 (activo) o 0 (inactivo)."
        }

    return {}


# =====================================================
# SERIALIZAR SERVICIO
# =====================================================

def serializar_servicio(servicio):
    """Convierte un servicio en un diccionario serializable."""

    if not servicio:
        return None

    return {
        "id_servicio": servicio.get("id_servicio"),
        "id_establecimiento": servicio.get("id_establecimiento"),
        "nombre": servicio.get("nombre"),
        "descripcion": servicio.get("descripcion"),
        "duracion_minutos": servicio.get("duracion_minutos"),
        "precio": (
            str(servicio.get("precio"))
            if servicio.get("precio") is not None
            else "0.00"
        ),
        "estado": servicio.get("estado")
    }


# =====================================================
# SERIALIZAR LISTA DE SERVICIOS
# =====================================================

def serializar_servicios(servicios):
    """Convierte una lista de servicios en datos serializables."""

    return [
        serializar_servicio(servicio)
        for servicio in servicios
    ]


# =====================================================
# SERIALIZAR SERVICIOS DISPONIBLES PARA CLIENTES
# =====================================================

def serializar_servicios_disponibles(servicios):
    """Serializa los servicios activos sin incluir datos administrativos."""

    return [
        {
            "id_servicio": servicio.get("id_servicio"),
            "id_establecimiento": servicio.get("id_establecimiento"),
            "nombre": servicio.get("nombre"),
            "descripcion": servicio.get("descripcion"),
            "duracion_minutos": servicio.get("duracion_minutos"),
            "precio": (
                str(servicio.get("precio"))
                if servicio.get("precio") is not None
                else "0.00"
            )
        }
        for servicio in servicios
    ]