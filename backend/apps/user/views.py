
from flask import jsonify, request

from apps.user import services
from apps.authentication import services as auth_services
from apps.appointments import services as appointments_services


# =====================================================
# RESPUESTA HTTP
# =====================================================

def respuesta_http(resultado, codigo_exito=200, codigo_error=400):
    """Convierte la respuesta del servicio en una respuesta HTTP."""

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible procesar la solicitud."
        }), 500

    codigo = codigo_exito if resultado.get("ok") else codigo_error

    return jsonify(resultado), codigo


# =====================================================
# OBTENER CLIENTE AUTENTICADO
# =====================================================

def obtener_cliente_autenticado():
    """Valida que la sesión corresponda a un cliente."""

    token = request.cookies.get("access_token")

    if not token:
        return None, (jsonify({
            "ok": False,
            "mensaje": "Debes iniciar sesión."
        }), 401)

    try:
        resultado = auth_services.validar_sesion(token)

    except Exception:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible verificar la sesión."
        }), 500)

    if not isinstance(resultado, dict) or not resultado.get("ok"):
        return None, (jsonify({
            "ok": False,
            "mensaje": "La sesión no es válida o ha expirado."
        }), 401)

    data = resultado.get("data") or {}

    if data.get("tipo_cuenta") != "cliente":
        return None, (jsonify({
            "ok": False,
            "mensaje": "Esta operación está disponible únicamente para clientes."
        }), 403)

    cliente = data.get("usuario")

    if not isinstance(cliente, dict):
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar al cliente."
        }), 401)

    return cliente, None


# =====================================================
# REGISTRAR CLIENTE
# =====================================================

def registrar_usuario():
    """Registra un cliente independiente."""

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos."
        }), 400

    # El cliente no puede asignarse a un establecimiento
    # ni elegir su cargo o estado.
    datos.pop("id_establecimiento", None)
    datos.pop("cargo", None)
    datos.pop("estado", None)

    resultado = services.registrar_usuario(datos)

    return respuesta_http(
        resultado,
        codigo_exito=201,
        codigo_error=400
    )


# =====================================================
# OBTENER CLIENTE
# =====================================================

def obtener_usuario(id_usuario):
    """Permite consultar únicamente el perfil propio."""

    cliente, error = obtener_cliente_autenticado()

    if error:
        return error

    if str(cliente.get("id_usuario")) != str(id_usuario):
        return jsonify({
            "ok": False,
            "mensaje": "No puedes consultar información de otro cliente."
        }), 403

    resultado = services.obtener_usuario(id_usuario)

    return respuesta_http(
        resultado,
        codigo_exito=200,
        codigo_error=404
    )


# =====================================================
# ACTUALIZAR CLIENTE
# =====================================================

def actualizar_usuario(id_usuario):
    """Permite actualizar únicamente los datos del perfil propio."""

    cliente, error = obtener_cliente_autenticado()

    if error:
        return error

    if str(cliente.get("id_usuario")) != str(id_usuario):
        return jsonify({
            "ok": False,
            "mensaje": "No puedes modificar información de otro cliente."
        }), 403

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos."
        }), 400

    campos_protegidos = {
        "id_usuario",
        "id_establecimiento",
        "cargo",
        "estado",
        "correo_verificado",
        "contrasena",
        "tipo_cuenta"
    }

    if campos_protegidos.intersection(datos.keys()):
        return jsonify({
            "ok": False,
            "mensaje": "No puedes modificar campos protegidos."
        }), 403

    resultado = services.actualizar_usuario(
        id_usuario,
        datos
    )

    return respuesta_http(resultado)



# =====================================================
# LISTAR CITAS DEL CLIENTE AUTENTICADO
# =====================================================

def listar_citas_usuario():
    """Consulta únicamente las citas del cliente autenticado."""

    cliente, error = obtener_cliente_autenticado()

    if error:
        return error

    id_usuario = cliente.get("id_usuario")

    if not id_usuario:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar al cliente."
        }), 401

    try:
        resultado = appointments_services.listar_citas_usuario(
            id_usuario
        )

        return respuesta_http(resultado)

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible consultar tus citas.",
            "data": None,
            "errores": {}
        }), 500
        


# =====================================================
# CREAR CITA DEL CLIENTE AUTENTICADO
# =====================================================

def crear_cita_usuario():
    """Registra una cita para el cliente autenticado."""

    cliente, error = obtener_cliente_autenticado()

    if error:
        return error

    id_usuario = cliente.get("id_usuario")

    if not id_usuario:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar al cliente."
        }), 401

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos."
        }), 400

    try:
        resultado = appointments_services.crear_cita_usuario(
            id_usuario,
            datos
        )

        return respuesta_http(
            resultado,
            codigo_exito=201,
            codigo_error=400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible registrar la cita.",
            "data": None,
            "errores": {}
        }), 500
