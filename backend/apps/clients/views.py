
from flask import Blueprint, request, jsonify

from apps.clients import services

from apps.establishment.views import (
    obtener_establecimiento_autenticado
)


# =====================================================
# BLUEPRINT
# =====================================================

clients_bp = Blueprint("clients", __name__)


# =====================================================
# RESPUESTA HTTP
# =====================================================

def respuesta_http(resultado, codigo_exito=200, codigo_error=400):

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Error interno al procesar la solicitud.",
            "data": None,
            "errores": {}
        }), 500

    codigo = (
        codigo_exito
        if resultado.get("ok")
        else codigo_error
    )

    return jsonify(resultado), codigo


# =====================================================
# OBTENER ID DEL ESTABLECIMIENTO AUTENTICADO
# =====================================================

def obtener_id_establecimiento():

    establecimiento, error = obtener_establecimiento_autenticado()

    if error:
        return None, error

    if not establecimiento:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No se encontró el establecimiento autenticado.",
            "data": None,
            "errores": {}
        }), 401)

    id_establecimiento = establecimiento.get("id_establecimiento")

    if not id_establecimiento:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento.",
            "data": None,
            "errores": {}
        }), 401)

    return id_establecimiento, None


# =====================================================
# LISTAR CLIENTES
# GET /api/clients/
# =====================================================

@clients_bp.route("/", methods=["GET"])
def listar_clientes():

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    resultado = services.listar_clientes(
        id_establecimiento
    )

    return respuesta_http(resultado)


# =====================================================
# CONSULTAR CLIENTE POR ID
# GET /api/clients/<id_cliente>
# =====================================================

@clients_bp.route("/<int:id_cliente>", methods=["GET"])
def consultar_cliente(id_cliente):

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    resultado, codigo = services.consultar_cliente(
        id_cliente,
        id_establecimiento
    )

    return jsonify(resultado), codigo


# =====================================================
# REGISTRAR CLIENTE
# POST /api/clients/
# =====================================================

@clients_bp.route("/", methods=["POST"])
def registrar_cliente():

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar los datos del cliente en formato JSON.",
            "data": None,
            "errores": {}
        }), 400

    resultado, codigo = services.registrar_cliente(
        datos,
        id_establecimiento
    )

    return jsonify(resultado), codigo


# =====================================================
# ACTUALIZAR CLIENTE
# PUT /api/clients/<id_cliente>
# =====================================================

@clients_bp.route("/<int:id_cliente>", methods=["PUT"])
def actualizar_cliente(id_cliente):

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar los datos del cliente en formato JSON.",
            "data": None,
            "errores": {}
        }), 400

    resultado, codigo = services.actualizar_cliente(
        id_cliente,
        datos,
        id_establecimiento
    )

    return jsonify(resultado), codigo


# =====================================================
# ELIMINAR CLIENTE
# DELETE /api/clients/<id_cliente>
# =====================================================

@clients_bp.route("/<int:id_cliente>", methods=["DELETE"])
def eliminar_cliente(id_cliente):

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    resultado, codigo = services.eliminar_cliente(
        id_cliente,
        id_establecimiento
    )

    return jsonify(resultado), codigo
