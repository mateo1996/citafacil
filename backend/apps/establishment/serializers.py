
import re


# =====================================================
# VALIDAR NOMBRE Y APELLIDO
# =====================================================

def validar_nombre(valor):
    """Comprueba que un nombre o apellido sea válido."""

    if not isinstance(valor, str):
        return False

    valor = valor.strip()

    return 2 <= len(valor) <= 50


# =====================================================
# VALIDAR NOMBRE COMERCIAL
# =====================================================

def validar_nombre_comercial(valor):
    """Comprueba que el nombre comercial sea válido."""

    if not isinstance(valor, str):
        return False

    valor = valor.strip()

    return 2 <= len(valor) <= 100


# =====================================================
# VALIDAR CORREO ELECTRÓNICO
# =====================================================

def validar_email(email):
    """Comprueba que el correo tenga un formato válido."""

    if not isinstance(email, str):
        return False

    email = email.strip()

    expresion = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return bool(re.match(expresion, email))



# =====================================================
# VALIDAR TELÉFONO
# =====================================================

def validar_telefono(telefono):
    """Comprueba que el teléfono tenga un formato válido."""

    if telefono is None or telefono == "":
        return True

    if not isinstance(telefono, str):
        return False

    telefono = telefono.strip()

    return (
        7 <= len(telefono) <= 20
        and bool(re.match(r"^[0-9+\-\s()]+$", telefono))
    )


# =====================================================
# VALIDAR DIRECCIÓN
# =====================================================

def validar_direccion(direccion):
    """Comprueba que la dirección sea válida."""

    if not isinstance(direccion, str):
        return False

    direccion = direccion.strip()

    return 3 <= len(direccion) <= 100


# =====================================================
# VALIDAR CONTRASEÑA
# =====================================================

def validar_contrasena(contrasena):
    """Comprueba que la contraseña cumpla la longitud permitida."""

    if not isinstance(contrasena, str):
        return False

    return 8 <= len(contrasena) <= 128


# =====================================================
# VALIDAR DATOS DEL ESTABLECIMIENTO
# =====================================================

def validar_datos_establecimiento(datos):
    """Valida los datos del establecimiento y su administrador."""

    errores = {}

    if not isinstance(datos, dict):
        return {
            "general": "Los datos del establecimiento no son válidos."
        }

    nombre = datos.get("nombre")
    apellido = datos.get("apellido")
    nombre_comercial = datos.get("nombre_establecimiento")
    telefono = datos.get("telefono")
    email = datos.get("email")
    direccion = datos.get("direccion")
    contrasena = datos.get("contrasena")

    if not validar_nombre(nombre):
        errores["nombre"] = (
            "El nombre debe tener entre 2 y 50 caracteres."
        )

    if not validar_nombre(apellido):
        errores["apellido"] = (
            "El apellido debe tener entre 2 y 50 caracteres."
        )

    if not validar_nombre_comercial(nombre_comercial):
        errores["nombre_establecimiento"] = (
            "El nombre comercial debe tener entre 2 y 100 caracteres."
        )

    if not validar_email(email):
        errores["email"] = (
            "Ingresa un correo electrónico válido."
        )

    if not validar_telefono(telefono):
        errores["telefono"] = (
            "El teléfono no tiene un formato válido."
        )

    if not validar_direccion(direccion):
        errores["direccion"] = (
            "La dirección debe tener entre 3 y 100 caracteres."
        )

    if not validar_contrasena(contrasena):
        errores["contrasena"] = (
            "La contraseña debe tener entre 8 y 128 caracteres."
        )

    return errores


# =====================================================
# SERIALIZAR ESTABLECIMIENTO
# =====================================================

def serializar_establecimiento(establecimiento):
    """Convierte un establecimiento en un diccionario serializable."""

    if not establecimiento:
        return None

    return {
        "id_establecimiento": establecimiento.get(
            "id_establecimiento"
        ),
        "nombre_comercial": establecimiento.get(
            "nombre_comercial"
        ),
        "nombre": establecimiento.get("nombre"),
        "apellido": establecimiento.get("apellido"),
        "telefono": establecimiento.get("telefono"),
        "email": establecimiento.get("email"),
        "direccion": establecimiento.get("direccion")
    }
