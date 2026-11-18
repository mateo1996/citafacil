
import re


# =====================================================
# VALIDAR ID DEL CLIENTE
# =====================================================

def validar_id_cliente(id_cliente):

    try:
        id_cliente = int(id_cliente)

        if id_cliente <= 0:
            return None

        return id_cliente

    except (TypeError, ValueError):
        return None


# =====================================================
# VALIDAR DATOS DEL CLIENTE
# =====================================================

def validar_datos_cliente(datos):

    errores = {}

    if not isinstance(datos, dict):
        return None, {
            "general": "Los datos del cliente deben ser un objeto válido."
        }

    # -------------------------------------------------
    # NOMBRE
    # -------------------------------------------------

    nombre = datos.get("nombre")

    if not isinstance(nombre, str) or not nombre.strip():

        errores["nombre"] = "El nombre del cliente es obligatorio."

    else:

        nombre = nombre.strip()

        if len(nombre) > 100:
            errores["nombre"] = "El nombre no puede superar los 100 caracteres."


    # -------------------------------------------------
    # TELÉFONO
    # -------------------------------------------------

    telefono = datos.get("telefono")

    if not isinstance(telefono, str) or not telefono.strip():

        errores["telefono"] = "El teléfono del cliente es obligatorio."

    else:

        telefono = telefono.strip()

        if len(telefono) > 20:
            errores["telefono"] = "El teléfono no puede superar los 20 caracteres."

        elif not re.fullmatch(r"[0-9+\-() ]+", telefono):
            errores["telefono"] = "El teléfono contiene caracteres no válidos."


    # -------------------------------------------------
    # CORREO
    # -------------------------------------------------

    correo = datos.get("correo")

    if correo is not None:

        if not isinstance(correo, str):

            errores["correo"] = "El correo debe ser un texto válido."

        else:

            correo = correo.strip()

            if correo == "":
                correo = None

            elif len(correo) > 100:
                errores["correo"] = "El correo no puede superar los 100 caracteres."

            elif not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                correo
            ):
                errores["correo"] = "El correo electrónico no tiene un formato válido."


    # -------------------------------------------------
    # RESULTADO
    # -------------------------------------------------

    if errores:
        return None, errores

    cliente = {
        "nombre": nombre,
        "telefono": telefono,
        "correo": correo
    }

    return cliente, {}


# =====================================================
# SERIALIZAR UN CLIENTE
# =====================================================

def serializar_cliente(cliente):

    if not cliente:
        return None

    return {
        "id_cliente": cliente.get("id_cliente"),
        "nombre": cliente.get("nombre"),
        "telefono": cliente.get("telefono"),
        "correo": cliente.get("correo")
    }


# =====================================================
# SERIALIZAR VARIOS CLIENTES
# =====================================================

def serializar_clientes(clientes):

    return [
        serializar_cliente(cliente)
        for cliente in clientes
    ]
