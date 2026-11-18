
from datetime import datetime, timedelta, timezone

import jwt

from config import settings


# =====================================================
# CONFIGURACIÓN JWT
# =====================================================

SECRET_KEY = settings.PASSWORD_JWT
JWT_ALGORITHM = settings.ALGORITHM_JWT


# =====================================================
# CREAR TOKEN JWT
# =====================================================

def create_jwt(payload: dict, exp_minutes: int = 60):
    """
    Genera un JWT firmado con la clave secreta configurada.
    """

    if not SECRET_KEY:
        raise RuntimeError(
            "No se ha configurado PASSWORD_JWT."
        )

    if not isinstance(payload, dict):
        raise ValueError(
            "El contenido del token debe ser un diccionario."
        )

    if not isinstance(exp_minutes, int) or isinstance(exp_minutes, bool):
        raise ValueError(
            "El tiempo de expiración debe ser un número entero."
        )

    if exp_minutes <= 0:
        raise ValueError(
            "El tiempo de expiración debe ser mayor que cero."
        )

    payload_copy = payload.copy()

    ahora = datetime.now(timezone.utc)

    payload_copy["iat"] = ahora
    payload_copy["exp"] = ahora + timedelta(
        minutes=exp_minutes
    )

    return jwt.encode(
        payload_copy,
        SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# =====================================================
# VALIDAR Y DESCODIFICAR TOKEN
# =====================================================

def decode_jwt(token: str):
    """
    Verifica la firma y la expiración del JWT.

    Devuelve el contenido del token si es válido.
    Devuelve None si es inválido o ha expirado.
    """

    if (
        not SECRET_KEY
        or not isinstance(token, str)
        or not token.strip()
    ):
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": ["exp", "iat"]
            }
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None
