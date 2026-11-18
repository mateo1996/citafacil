
import re

from config import settings


# =====================================================
# VALIDAR CORREO ELECTRÓNICO
# =====================================================

def validar_correo(correo):
    """Comprueba que el correo tenga un formato válido."""

    if not isinstance(correo, str):
        return False

    correo = correo.strip()

    expresion = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return re.fullmatch(expresion, correo) is not None


# =====================================================
# SERIALIZAR CLIENTE PARA RESPUESTAS
# =====================================================

def serializar_usuario(usuario):
    """Devuelve únicamente los datos públicos del cliente."""

    if not isinstance(usuario, dict):
        return None

    return {
        "id_usuario": usuario.get("id_usuario"),
        "id_establecimiento": usuario.get("id_establecimiento"),
        "nombre": usuario.get("nombre"),
        "correo": usuario.get("correo"),
        "telefono": usuario.get("telefono"),
        "cargo": usuario.get("cargo"),
        "estado": usuario.get("estado"),
        "correo_verificado": bool(
            usuario.get("correo_verificado", False)
        )
    }


# =====================================================
# SERIALIZAR LISTA DE CLIENTES
# =====================================================

def serializar_usuarios(usuarios):
    """Serializa una lista de clientes."""

    if not isinstance(usuarios, (list, tuple)):
        return []

    return [
        serializar_usuario(usuario)
        for usuario in usuarios
        if isinstance(usuario, dict)
    ]


# =====================================================
# VALIDAR DATOS DE REGISTRO
# =====================================================

def validar_datos_registro(datos):
    """Valida los datos necesarios para registrar un cliente."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos recibidos no tienen un formato válido."
        }

    nombre = datos.get("nombre")
    correo = datos.get("correo")
    telefono = datos.get("telefono")
    contrasena = datos.get("contrasena")
    confirmar_contrasena = datos.get("confirmar_contrasena")

    # VALIDAR NOMBRE

    if not isinstance(nombre, str) or len(nombre.strip()) < 3:
        errores["nombre"] = (
            "El nombre debe tener al menos 3 caracteres."
        )

    # VALIDAR CORREO

    if not isinstance(correo, str) or not validar_correo(correo):
        errores["correo"] = (
            "El correo electrónico no es válido."
        )

    # VALIDAR TELÉFONO

    if telefono is not None and not isinstance(telefono, str):

        errores["telefono"] = (
            "El teléfono debe ser un texto válido."
        )

    elif isinstance(telefono, str) and telefono.strip():

        if not re.fullmatch(
            r"[0-9+\-\s()]{7,20}",
            telefono.strip()
        ):
            errores["telefono"] = (
                "El teléfono no tiene un formato válido."
            )

    # VALIDAR CONTRASEÑA

    if not isinstance(contrasena, str):

        errores["contrasena"] = (
            "La contraseña debe ser un texto válido."
        )

    else:

        if len(contrasena) < settings.PASSWORD_MIN_LENGTH:
            errores["contrasena"] = (
                f"La contraseña debe tener al menos "
                f"{settings.PASSWORD_MIN_LENGTH} caracteres."
            )

        elif len(contrasena.encode("utf-8")) > 72:
            errores["contrasena"] = (
                "La contraseña supera el límite permitido."
            )

    # CONFIRMAR CONTRASEÑA

    if not isinstance(confirmar_contrasena, str):

        errores["confirmar_contrasena"] = (
            "Debes confirmar tu contraseña."
        )

    elif (
        isinstance(contrasena, str)
        and contrasena != confirmar_contrasena
    ):
        errores["confirmar_contrasena"] = (
            "Las contraseñas no coinciden."
        )

    return errores


# =====================================================
# VALIDAR DATOS DE ACTUALIZACIÓN
# =====================================================

def validar_datos_actualizacion(datos):
    """Valida los datos permitidos para actualizar un cliente."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos recibidos no tienen un formato válido."
        }

    nombre = datos.get("nombre")
    correo = datos.get("correo")
    telefono = datos.get("telefono")

    # VALIDAR NOMBRE

    if not isinstance(nombre, str) or len(nombre.strip()) < 3:
        errores["nombre"] = (
            "El nombre debe tener al menos 3 caracteres."
        )

    # VALIDAR CORREO

    if not isinstance(correo, str) or not validar_correo(correo):
        errores["correo"] = (
            "El correo electrónico no es válido."
        )

    # VALIDAR TELÉFONO

    if telefono is not None and not isinstance(telefono, str):

        errores["telefono"] = (
            "El teléfono debe ser un texto válido."
        )

    elif isinstance(telefono, str) and telefono.strip():

        if not re.fullmatch(
            r"[0-9+\-\s()]{7,20}",
            telefono.strip()
        ):
            errores["telefono"] = (
                "El teléfono no tiene un formato válido."
            )

    return errores
