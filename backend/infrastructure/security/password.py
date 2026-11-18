
import bcrypt


# =====================================================
# GENERAR HASH DE CONTRASEÑA
# =====================================================

def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña.

    La contraseña original nunca se almacena.
    """

    if not isinstance(password, str) or not password:
        raise ValueError(
            "La contraseña no es válida."
        )

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "La contraseña supera el límite permitido por bcrypt."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


# =====================================================
# VERIFICAR CONTRASEÑA
# =====================================================

def check_password(password: str, hashed: str) -> bool:
    """
    Comprueba si una contraseña coincide con un hash bcrypt.
    """

    if not isinstance(password, str) or not isinstance(hashed, str):
        return False

    if not password or not hashed:
        return False

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            hashed.encode("utf-8")
        )

    except (ValueError, TypeError):
        return False
