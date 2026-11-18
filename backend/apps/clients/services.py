
from apps.clients import repositories
from apps.whatsapp.conversation import normalizar_telefono

from apps.clients.serializers import (
    validar_id_cliente,
    validar_datos_cliente,
    serializar_cliente,
    serializar_clientes
)


# =====================================================
# ESTRUCTURA DE RESPUESTA
# =====================================================

def respuesta(ok, mensaje, data=None, errores=None):

    return {
        "ok": ok,
        "mensaje": mensaje,
        "data": data,
        "errores": errores or {}
    }


# =====================================================
# LISTAR CLIENTES
# =====================================================

def listar_clientes(id_establecimiento):

    try:

        clientes = repositories.obtener_todos_los_clientes(
            id_establecimiento
        )

        return respuesta(
            True,
            "Clientes consultados correctamente.",
            serializar_clientes(clientes)
        )

    except Exception as error:

        print(f"Error al listar clientes: {error}")

        return respuesta(
            False,
            "No fue posible consultar los clientes."
        )


# =====================================================
# CONSULTAR CLIENTE POR ID
# =====================================================

def consultar_cliente(id_cliente, id_establecimiento):

    id_cliente = validar_id_cliente(id_cliente)

    if id_cliente is None:

        return respuesta(
            False,
            "El identificador del cliente no es válido.",
            errores={
                "id_cliente": "Debe ser un número entero positivo."
            }
        ), 400

    try:

        cliente = repositories.obtener_cliente_por_id(
            id_cliente,
            id_establecimiento
        )

        if not cliente:

            return respuesta(
                False,
                "El cliente no existe."
            ), 404

        return respuesta(
            True,
            "Cliente consultado correctamente.",
            serializar_cliente(cliente)
        ), 200

    except Exception as error:

        print(f"Error al consultar cliente: {error}")

        return respuesta(
            False,
            "No fue posible consultar el cliente."
        ), 500


# =====================================================
# REGISTRAR CLIENTE
# =====================================================

def registrar_cliente(datos, id_establecimiento):

    cliente, errores = validar_datos_cliente(datos)

    if errores:

        return respuesta(
            False,
            "Los datos del cliente no son válidos.",
            errores=errores
        ), 400

    try:

        # Comprobar si el teléfono ya está registrado
        cliente_existente = repositories.obtener_cliente_por_telefono(
            cliente["telefono"],
            id_establecimiento
        )

        if cliente_existente:

            return respuesta(
                False,
                "Ya existe un cliente con ese teléfono en este establecimiento.",
                errores={
                    "telefono": "Este número de teléfono ya está registrado."
                }
            ), 409

        id_cliente = repositories.crear_cliente(
            id_establecimiento=id_establecimiento,
            nombre=cliente["nombre"],
            telefono=cliente["telefono"],
            correo=cliente["correo"]
        )

        nuevo_cliente = repositories.obtener_cliente_por_id(
            id_cliente,
            id_establecimiento
        )

        return respuesta(
            True,
            "Cliente registrado correctamente.",
            serializar_cliente(nuevo_cliente)
        ), 201

    except Exception as error:

        print(f"Error al registrar cliente: {error}")

        return respuesta(
            False,
            "No fue posible registrar el cliente."
        ), 500


# =====================================================
# ACTUALIZAR CLIENTE
# =====================================================

def actualizar_cliente(id_cliente, datos, id_establecimiento):

    id_cliente = validar_id_cliente(id_cliente)

    if id_cliente is None:

        return respuesta(
            False,
            "El identificador del cliente no es válido.",
            errores={
                "id_cliente": "Debe ser un número entero positivo."
            }
        ), 400

    cliente, errores = validar_datos_cliente(datos)

    if errores:

        return respuesta(
            False,
            "Los datos del cliente no son válidos.",
            errores=errores
        ), 400

    try:

        cliente_existente = repositories.obtener_cliente_por_id(
            id_cliente,
            id_establecimiento
        )

        if not cliente_existente:

            return respuesta(
                False,
                "El cliente no existe."
            ), 404

        # Evitar que dos clientes del mismo establecimiento
        # tengan el mismo número de teléfono.
        cliente_telefono = repositories.obtener_cliente_por_telefono(
            cliente["telefono"],
            id_establecimiento
        )

        if (
            cliente_telefono
            and cliente_telefono["id_cliente"] != id_cliente
        ):

            return respuesta(
                False,
                "Ya existe otro cliente con ese teléfono.",
                errores={
                    "telefono": "Este número ya pertenece a otro cliente."
                }
            ), 409

        actualizado = repositories.actualizar_cliente(
            id_cliente=id_cliente,
            id_establecimiento=id_establecimiento,
            nombre=cliente["nombre"],
            telefono=cliente["telefono"],
            correo=cliente["correo"]
        )

        if not actualizado:

            return respuesta(
                False,
                "No fue posible actualizar el cliente."
            ), 404

        cliente_actualizado = repositories.obtener_cliente_por_id(
            id_cliente,
            id_establecimiento
        )

        return respuesta(
            True,
            "Cliente actualizado correctamente.",
            serializar_cliente(cliente_actualizado)
        ), 200

    except Exception as error:

        print(f"Error al actualizar cliente: {error}")

        return respuesta(
            False,
            "No fue posible actualizar el cliente."
        ), 500


# =====================================================
# ELIMINAR CLIENTE
# =====================================================

def eliminar_cliente(id_cliente, id_establecimiento):

    id_cliente = validar_id_cliente(id_cliente)

    if id_cliente is None:

        return respuesta(
            False,
            "El identificador del cliente no es válido.",
            errores={
                "id_cliente": "Debe ser un número entero positivo."
            }
        ), 400

    try:

        cliente = repositories.obtener_cliente_por_id(
            id_cliente,
            id_establecimiento
        )

        if not cliente:

            return respuesta(
                False,
                "El cliente no existe."
            ), 404

        eliminado = repositories.eliminar_cliente(
            id_cliente,
            id_establecimiento
        )

        if not eliminado:

            return respuesta(
                False,
                "No fue posible eliminar el cliente."
            ), 404

        return respuesta(
            True,
            "Cliente eliminado correctamente."
        ), 200

    except Exception as error:

        print(f"Error al eliminar cliente: {error}")

        return respuesta(
            False,
            "No fue posible eliminar el cliente. Puede tener citas asociadas."
        ), 500


# =====================================================
# BUSCAR CLIENTE POR TELÉFONO
# =====================================================

def buscar_cliente(remitente, id_establecimiento):

    from apps.clients import repositories

    telefono = normalizar_telefono(remitente)

    try:

        cliente = repositories.obtener_cliente_por_telefono(
            telefono,
            id_establecimiento
        )

        return cliente

    except Exception as error:

        print(f"Error al buscar cliente desde WhatsApp: {error}")

        return None