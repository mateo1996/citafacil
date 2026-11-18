
from flask import jsonify, request, make_response

from config import settings
from apps.authentication import services


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def _obtener_datos():
    """
    Obtiene los datos JSON enviados por el frontend.
    Si no se recibe un JSON válido, devuelve un diccionario vacío.
    """
    return request.get_json(silent=True) or {}


def _crear_respuesta(
    resultado,
    codigo_exito=200,
    codigo_error=400
):
    """
    Convierte la respuesta del servicio en una respuesta HTTP.
    """

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible procesar la solicitud."
        }), 500

    codigo = (
        codigo_exito
        if resultado.get("ok")
        else codigo_error
    )

    return jsonify(resultado), codigo


# =====================================================
# INICIAR SESIÓN
# =====================================================

def iniciar_sesion():
    """
    Autentica al usuario y establece una cookie HttpOnly
    cuando el servicio devuelve un JWT.
    """

    datos = _obtener_datos()

    resultado = services.iniciar_sesion(datos)

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Error al procesar el inicio de sesión."
        }), 500

    if not resultado.get("ok"):
        return jsonify(resultado), 401

    data = resultado.get("data") or {}
    token = data.get("token")

    if not token:
        return jsonify({
            "ok": False,
            "mensaje": "No se recibió el token de autenticación."
        }), 500

    respuesta = make_response(jsonify(resultado))

    respuesta.set_cookie(
        "access_token",
        token,
        max_age=settings.JWT_EXP_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/"
    )

    return respuesta


# =====================================================
# VERIFICAR CORREO ELECTRÓNICO
# =====================================================

def verificar_correo():
    """
    Verifica la dirección de correo mediante el token
    enviado al usuario.
    """

    datos = _obtener_datos()
    token = datos.get("token")

    if not token:
        return jsonify({
            "ok": False,
            "mensaje": "No se proporcionó el token de verificación."
        }), 400

    resultado = services.verificar_correo_usuario(token)

    return _crear_respuesta(resultado)


# =====================================================
# SOLICITAR RECUPERACIÓN DE CONTRASEÑA
# =====================================================

def solicitar_recuperacion():
    """
    Solicita el envío de un correo para recuperar
    la contraseña de la cuenta.
    """

    datos = _obtener_datos()

    resultado = services.solicitar_recuperacion_contrasena(datos)

    return _crear_respuesta(resultado)


# =====================================================
# RESTABLECER CONTRASEÑA
# =====================================================

def restablecer_contrasena():
    """
    Permite establecer una nueva contraseña utilizando
    el token de recuperación.
    """

    datos = _obtener_datos()

    resultado = services.restablecer_contrasena(datos)

    return _crear_respuesta(resultado)


# =====================================================
# VALIDAR SESIÓN
# =====================================================

def validar_sesion():
    """
    Comprueba si existe una sesión válida mediante
    el JWT almacenado en la cookie HttpOnly.
    """

    token = request.cookies.get("access_token")

    if not token:
        return jsonify({
            "ok": False,
            "mensaje": "No existe una sesión activa."
        }), 401

    resultado = services.validar_sesion(token)

    return _crear_respuesta(
        resultado,
        codigo_exito=200,
        codigo_error=401
    )


# =====================================================
# CERRAR SESIÓN
# =====================================================

def cerrar_sesion():
    """
    Elimina la cookie de autenticación del navegador.
    """

    respuesta = make_response(jsonify({
        "ok": True,
        "mensaje": "Sesión cerrada correctamente."
    }))

    respuesta.delete_cookie(
        "access_token",
        path="/",
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite=settings.SESSION_COOKIE_SAMESITE
    )

    return respuesta
