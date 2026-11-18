from config import settings
import re


# =====================================================
# VALIDAR CORREO ELECTRÓNICO
# =====================================================

def validar_correo(correo: str) -> bool:
    """Comprueba que el correo tenga un formato válido."""

    if not isinstance(correo, str):
        return False

    correo = correo.strip()

    patron = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return bool(re.match(patron, correo))


# =====================================================
# VALIDAR CREDENCIALES
# =====================================================

def validar_credenciales(datos: dict) -> dict:
    """Valida los datos necesarios para iniciar sesión."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "valido": False,
            "errores": {
                "general": "Los datos recibidos no son válidos."
            }
        }

    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not isinstance(correo, str) or not correo.strip():
        errores["correo"] = "El correo electrónico es obligatorio."

    elif not validar_correo(correo):
        errores["correo"] = (
            "El correo electrónico no tiene un formato válido."
        )

    if not isinstance(contrasena, str) or not contrasena:
        errores["contrasena"] = "La contraseña es obligatoria."

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


# =====================================================
# VALIDAR TOKEN
# =====================================================

def validar_token(datos: dict) -> dict:
    """Valida la estructura de una solicitud que contiene un token."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "valido": False,
            "errores": {
                "general": "Los datos recibidos no son válidos."
            }
        }

    token = datos.get("token")

    if not isinstance(token, str) or not token.strip():
        errores["token"] = "El token es obligatorio."

    elif len(token) > 4096:
        errores["token"] = (
            "El token tiene un tamaño no permitido."
        )

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


# =====================================================
# VALIDAR SOLICITUD DE RECUPERACIÓN
# =====================================================

def validar_solicitud_recuperacion(datos: dict) -> dict:
    """Valida los datos para solicitar recuperación de contraseña."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "valido": False,
            "errores": {
                "general": "Los datos recibidos no son válidos."
            }
        }

    correo = datos.get("correo")

    if not isinstance(correo, str) or not correo.strip():
        errores["correo"] = "El correo electrónico es obligatorio."

    elif not validar_correo(correo):
        errores["correo"] = (
            "El correo electrónico no tiene un formato válido."
        )

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


# =====================================================
# VALIDAR NUEVA CONTRASEÑA
# =====================================================

def validar_nueva_contrasena(datos: dict) -> dict:
    """Valida la nueva contraseña y su confirmación."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "valido": False,
            "errores": {
                "general": "Los datos recibidos no son válidos."
            }
        }

    nueva_contrasena = datos.get("nueva_contrasena")
    confirmar_contrasena = datos.get("confirmar_contrasena")

    if not isinstance(nueva_contrasena, str) or not nueva_contrasena:

        errores["nueva_contrasena"] = (
            "La nueva contraseña es obligatoria."
        )

    else:
        if len(nueva_contrasena) < settings.PASSWORD_MIN_LENGTH:
            errores["nueva_contrasena"] = (
                f"La contraseña debe tener al menos "
                f"{settings.PASSWORD_MIN_LENGTH} caracteres."
            )

        elif len(nueva_contrasena.encode("utf-8")) > 72:
            errores["nueva_contrasena"] = (
                "La contraseña supera el límite permitido por bcrypt."
            )

    if (
        not isinstance(confirmar_contrasena, str)
        or not confirmar_contrasena
    ):
        errores["confirmar_contrasena"] = (
            "Debes confirmar la nueva contraseña."
        )

    elif nueva_contrasena != confirmar_contrasena:
        errores["confirmar_contrasena"] = (
            "Las contraseñas no coinciden."
        )

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }
