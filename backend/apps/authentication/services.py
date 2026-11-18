
import logging
import secrets

from datetime import datetime, timedelta, timezone

from config import settings

from apps.user import repositories as user_repository
from apps.user.serializers import serializar_usuario

from apps.authentication import repositories as auth_repository
from apps.authentication import serializers as auth_serializers

from infrastructure.security.password import (
    hash_password,
    check_password
)

from infrastructure.security.jwt import (
    create_jwt,
    decode_jwt
)

from infrastructure.external.email.email import (
    send_verification_email,
    send_password_reset_email
)


logger = logging.getLogger(__name__)


# =====================================================
# RESPUESTA GENERAL
# =====================================================

def respuesta(
    ok: bool,
    mensaje: str,
    data=None,
    errores=None
) -> dict:
    """Estandariza las respuestas del servicio."""

    return {
        "ok": ok,
        "mensaje": mensaje,
        "data": data,
        "errores": errores
    }


# =====================================================
# UTILIDADES INTERNAS
# =====================================================

def _obtener_campo(usuario: dict, *nombres):
    """Obtiene un campo contemplando los nombres de MySQL."""

    if not isinstance(usuario, dict):
        return None

    for nombre in nombres:
        if nombre in usuario:
            return usuario[nombre]

    return None


def _generar_token_aleatorio() -> str:
    """Genera un token aleatorio para operaciones de un solo uso."""

    return secrets.token_urlsafe(32)


def _obtener_fecha_utc() -> datetime:
    """Obtiene la fecha y hora actual en UTC."""

    return datetime.now(timezone.utc)


# =====================================================
# INICIO DE SESIÓN
# =====================================================

def iniciar_sesion(datos: dict) -> dict:
    """Autentica clientes y establecimientos."""

    # ---------------------------------------------
    # VALIDAR CREDENCIALES
    # ---------------------------------------------

    validacion = auth_serializers.validar_credenciales(datos)

    if not validacion["valido"]:
        return respuesta(
            False,
            "Los datos ingresados no son válidos.",
            errores=validacion["errores"]
        )

    correo = datos["correo"].strip().lower()
    contrasena = datos["contrasena"]

    # ---------------------------------------------
    # BUSCAR EN AMBAS TABLAS
    # ---------------------------------------------

    cliente = user_repository.obtener_usuario_por_correo(correo)

    establecimiento = (
        user_repository.obtener_establecimiento_por_correo(correo)
    )

    # Evitar ambigüedad entre dos cuentas.
    if cliente and establecimiento:
        logger.error(
            "El correo %s está registrado en ambas tablas.",
            correo
        )

        return respuesta(
            False,
            "No fue posible identificar el tipo de cuenta."
        )

    if not cliente and not establecimiento:
        return respuesta(
            False,
            "Correo o contraseña incorrectos."
        )

    # ---------------------------------------------
    # IDENTIFICAR TIPO DE CUENTA
    # ---------------------------------------------

    if cliente:
        cuenta = cliente
        tipo_cuenta = "cliente"

        id_usuario = cuenta.get("id_usuario")
        id_establecimiento = None

        nombre = cuenta.get("nombre")
        correo_cuenta = cuenta.get("correo")

        contrasena_hash = cuenta.get("contrasena")

    else:
        cuenta = establecimiento
        tipo_cuenta = "establecimiento"

        id_usuario = None
        id_establecimiento = cuenta.get("id_establecimiento")

        nombre = cuenta.get("nombre_comercial")
        correo_cuenta = cuenta.get("email")

        contrasena_hash = cuenta.get("contrasena")

    # ---------------------------------------------
    # COMPROBAR IDENTIFICADOR
    # ---------------------------------------------

    if tipo_cuenta == "cliente" and not id_usuario:
        return respuesta(
            False,
            "No fue posible identificar al cliente."
        )

    if tipo_cuenta == "establecimiento" and not id_establecimiento:
        return respuesta(
            False,
            "No fue posible identificar al establecimiento."
        )

    # ---------------------------------------------
    # COMPROBAR CONTRASEÑA
    # ---------------------------------------------

    if not contrasena_hash:
        return respuesta(
            False,
            "Correo o contraseña incorrectos."
        )

    if not check_password(contrasena, contrasena_hash):
        return respuesta(
            False,
            "Correo o contraseña incorrectos."
        )

    # ---------------------------------------------
    # COMPROBAR VERIFICACIÓN DEL CORREO
    # ---------------------------------------------

    correo_verificado = cuenta.get("correo_verificado")

    if not bool(correo_verificado):
        return respuesta(
            False,
            "Debes verificar tu correo electrónico antes de iniciar sesión."
        )

    # ---------------------------------------------
    # COMPROBAR ESTADO DE LA CUENTA
    # ---------------------------------------------

    estado = cuenta.get("estado")

    if estado != 1:
        return respuesta(
            False,
            "La cuenta no está activa."
        )

    # ---------------------------------------------
    # GENERAR JWT
    # ---------------------------------------------

    payload = {
        "tipo": "access",
        "tipo_cuenta": tipo_cuenta,
        "id_usuario": id_usuario,
        "id_establecimiento": id_establecimiento,
        "correo": correo_cuenta,
        "cargo": "cliente" if tipo_cuenta == "cliente" else "establecimiento"
    }

    token = create_jwt(
        payload,
        exp_minutes=settings.JWT_EXP_DAYS * 24 * 60
    )

    # ---------------------------------------------
    # PREPARAR DATOS DE LA CUENTA
    # ---------------------------------------------

    if tipo_cuenta == "cliente":

        datos_cuenta = {
            "id_usuario": id_usuario,
            "id_establecimiento": cuenta.get("id_establecimiento"),
            "nombre": nombre,
            "correo": correo_cuenta,
            "telefono": cuenta.get("telefono"),
            "cargo": "cliente",
            "estado": estado,
            "correo_verificado": True
        }

    else:

        datos_cuenta = {
            "id_establecimiento": id_establecimiento,
            "nombre_comercial": cuenta.get("nombre_comercial"),
            "nombre": cuenta.get("nombre"),
            "apellido": cuenta.get("apellido"),
            "telefono": cuenta.get("telefono"),
            "email": correo_cuenta,
            "direccion": cuenta.get("direccion"),
            "estado": estado,
            "correo_verificado": True
        }

    # ---------------------------------------------
    # RESPUESTA
    # ---------------------------------------------

    return respuesta(
        True,
        "Inicio de sesión exitoso.",
        data={
            "token": token,
            "tipo_cuenta": tipo_cuenta,
            "usuario": datos_cuenta
        }
    )



# =====================================================
# ENVÍO DE VERIFICACIÓN DE CORREO
# =====================================================

def enviar_verificacion_correo(
    correo: str,
    nombre: str,
    id_usuario: int = None,
    id_establecimiento: int = None
) -> bool:
    """
    Genera, almacena y envía un token de verificación
    para clientes o establecimientos.
    """

    try:
        # ---------------------------------------------
        # VALIDAR PROPIETARIO
        # ---------------------------------------------

        if (id_usuario is None) == (id_establecimiento is None):
            raise ValueError(
                "Debe indicarse un cliente o un establecimiento."
            )

        token = _generar_token_aleatorio()

        fecha_expiracion = _obtener_fecha_utc() + timedelta(
            minutes=settings.JWT_EMAIL_VERIFICATION_MINUTES
        )

        # ---------------------------------------------
        # INVALIDAR TOKENS ANTERIORES
        # ---------------------------------------------

        if id_usuario is not None:

            auth_repository.invalidar_tokens_usuario(
                id_usuario,
                "verificacion_email"
            )

        else:

            auth_repository.invalidar_tokens_establecimiento(
                id_establecimiento,
                "verificacion_email"
            )

        # ---------------------------------------------
        # GUARDAR TOKEN
        # ---------------------------------------------

        auth_repository.guardar_token(
            id_usuario,
            token,
            "verificacion_email",
            fecha_expiracion,
            id_establecimiento=id_establecimiento
        )

        # ---------------------------------------------
        # ENVIAR CORREO
        # ---------------------------------------------

        enviado = send_verification_email(
            correo,
            nombre,
            token
        )

        if not enviado:

            if id_usuario is not None:
                auth_repository.invalidar_tokens_usuario(
                    id_usuario,
                    "verificacion_email"
                )
            else:
                auth_repository.invalidar_tokens_establecimiento(
                    id_establecimiento,
                    "verificacion_email"
                )

            return False

        return True

    except Exception:

        logger.exception(
            "Error al enviar el correo de verificación."
        )

        try:
            if id_usuario is not None:
                auth_repository.invalidar_tokens_usuario(
                    id_usuario,
                    "verificacion_email"
                )

            elif id_establecimiento is not None:
                auth_repository.invalidar_tokens_establecimiento(
                    id_establecimiento,
                    "verificacion_email"
                )

        except Exception:
            logger.exception(
                "No fue posible invalidar el token de verificación."
            )

        return False




# =====================================================
# VERIFICAR CORREO
# =====================================================

def verificar_correo_usuario(token: str) -> dict:
    """Verifica el correo de un cliente o establecimiento."""

    if not token or not isinstance(token, str):
        return respuesta(
            False,
            "El enlace de verificación no es válido."
        )

    try:
        resultado = auth_repository.consumir_token_verificacion(
            token.strip()
        )

        if not resultado:
            return respuesta(
                False,
                "El enlace de verificación es inválido o ha expirado."
            )

        id_usuario = resultado.get("id_usuario")
        id_establecimiento = resultado.get("id_establecimiento")

        # ---------------------------------------------
        # INVALIDAR OTROS TOKENS DEL MISMO PROPIETARIO
        # ---------------------------------------------

        if id_usuario is not None:

            auth_repository.invalidar_tokens_usuario(
                id_usuario,
                "verificacion_email"
            )

            tipo_cuenta = "cliente"

        elif id_establecimiento is not None:

            auth_repository.invalidar_tokens_establecimiento(
                id_establecimiento,
                "verificacion_email"
            )

            tipo_cuenta = "establecimiento"

        else:
            logger.error(
                "El token consumido no tiene un propietario válido."
            )

            return respuesta(
                False,
                "No fue posible completar la verificación."
            )

        return respuesta(
            True,
            "Correo electrónico verificado correctamente.",
            data={
                "tipo_cuenta": tipo_cuenta,
                "id_usuario": id_usuario,
                "id_establecimiento": id_establecimiento
            }
        )

    except Exception:

        logger.exception(
            "Error al verificar el correo electrónico."
        )

        return respuesta(
            False,
            "Ocurrió un error al verificar el correo."
        )




# =====================================================
# SOLICITAR RECUPERACIÓN DE CONTRASEÑA
# =====================================================

def solicitar_recuperacion_contrasena(datos: dict) -> dict:
    """Solicita recuperación para clientes y establecimientos."""

    validacion = auth_serializers.validar_solicitud_recuperacion(
        datos
    )

    if not validacion["valido"]:
        return respuesta(
            False,
            "Los datos ingresados no son válidos.",
            errores=validacion["errores"]
        )

    correo = datos["correo"].strip().lower()

    try:
        cliente = user_repository.obtener_usuario_por_correo(correo)

        establecimiento = (
            user_repository.obtener_establecimiento_por_correo(correo)
        )

        # Evitar ambigüedad entre los dos tipos de cuenta.
        if cliente and establecimiento:
            logger.error(
                "El correo %s está registrado en ambas tablas.",
                correo
            )
            return respuesta(
                True,
                "Si la cuenta existe, recibirás instrucciones para recuperar tu contraseña."
            )

        if cliente:
            id_usuario = cliente.get("id_usuario")
            id_establecimiento = None
            nombre = cliente.get("nombre")

        elif establecimiento:
            id_usuario = None
            id_establecimiento = establecimiento.get(
                "id_establecimiento"
            )
            nombre = establecimiento.get("nombre_comercial")

        else:
            return respuesta(
                True,
                "Si la cuenta existe, recibirás instrucciones para recuperar tu contraseña."
            )

        token = _generar_token_aleatorio()

        fecha_expiracion = _obtener_fecha_utc() + timedelta(
            minutes=settings.JWT_PASSWORD_RESET_MINUTES
        )

        # Invalidar tokens anteriores.
        if id_usuario is not None:
            auth_repository.invalidar_tokens_usuario(
                id_usuario,
                "recuperacion_password"
            )
        else:
            auth_repository.invalidar_tokens_establecimiento(
                id_establecimiento,
                "recuperacion_password"
            )

        # Guardar el token.
        auth_repository.guardar_token(
            id_usuario,
            token,
            "recuperacion_password",
            fecha_expiracion,
            id_establecimiento=id_establecimiento
        )

        # Enviar correo.
        enviado = send_password_reset_email(
            correo,
            nombre,
            token
        )

        if not enviado:
            if id_usuario is not None:
                auth_repository.invalidar_tokens_usuario(
                    id_usuario,
                    "recuperacion_password"
                )
            else:
                auth_repository.invalidar_tokens_establecimiento(
                    id_establecimiento,
                    "recuperacion_password"
                )

            return respuesta(
                False,
                "No fue posible enviar el correo de recuperación."
            )

        return respuesta(
            True,
            "Si la cuenta existe, recibirás instrucciones para recuperar tu contraseña."
        )

    except Exception:
        logger.exception(
            "Error al solicitar recuperación de contraseña."
        )

        return respuesta(
            False,
            "Ocurrió un error al solicitar la recuperación."
        )



# =====================================================
# RESTABLECER CONTRASEÑA
# =====================================================

def restablecer_contrasena(datos: dict) -> dict:
    """Restablece la contraseña de clientes o establecimientos."""

    validacion_token = auth_serializers.validar_token(datos)

    if not validacion_token["valido"]:
        return respuesta(
            False,
            "El token no es válido.",
            errores=validacion_token["errores"]
        )

    validacion_contrasena = (
        auth_serializers.validar_nueva_contrasena(datos)
    )

    if not validacion_contrasena["valido"]:
        return respuesta(
            False,
            "La nueva contraseña no es válida.",
            errores=validacion_contrasena["errores"]
        )

    try:
        token = datos["token"].strip()

        resultado = auth_repository.obtener_token_valido(
            token,
            "recuperacion_password"
        )

        if not resultado:
            return respuesta(
                False,
                "El enlace de recuperación es inválido o ha expirado."
            )

        id_usuario = resultado.get("ID_USUARIO")
        id_establecimiento = resultado.get("ID_ESTABLECIMIENTO")

        # Comprobar que exista un único propietario.
        if (id_usuario is None) == (id_establecimiento is None):
            logger.error(
                "Token de recuperación con propietario inválido."
            )
            return respuesta(
                False,
                "No fue posible identificar la cuenta."
            )

        nueva_contrasena = datos["nueva_contrasena"]
        nuevo_hash = hash_password(nueva_contrasena)

        # Consumir el token antes de actualizar la contraseña.
        token_consumido = auth_repository.consumir_token(
            token,
            "recuperacion_password"
        )

        if not token_consumido:
            return respuesta(
                False,
                "El enlace ya fue utilizado o ha expirado."
            )

        if id_usuario is not None:

            actualizado = user_repository.actualizar_contrasena(
                id_usuario,
                nuevo_hash
            )

            if actualizado:
                auth_repository.invalidar_tokens_usuario(
                    id_usuario,
                    "recuperacion_password"
                )

        else:

            actualizado = (
                user_repository.actualizar_contrasena_establecimiento(
                    id_establecimiento,
                    nuevo_hash
                )
            )

            if actualizado:
                auth_repository.invalidar_tokens_establecimiento(
                    id_establecimiento,
                    "recuperacion_password"
                )

        if not actualizado:
            logger.error(
                "No fue posible actualizar la contraseña."
            )
            return respuesta(
                False,
                "No fue posible actualizar la contraseña."
            )

        return respuesta(
            True,
            "La contraseña se restableció correctamente."
        )

    except Exception:
        logger.exception(
            "Error al restablecer la contraseña."
        )

        return respuesta(
            False,
            "Ocurrió un error al restablecer la contraseña."
        )



# =====================================================
# VALIDACIÓN DE SESIÓN
# =====================================================

def validar_sesion(token: str) -> dict:
    """Valida la sesión de clientes y establecimientos."""

    if not isinstance(token, str) or not token:
        return respuesta(
            False,
            "No se proporcionó un token de autenticación."
        )

    payload = decode_jwt(token)

    if not payload or payload.get("tipo") != "access":
        return respuesta(
            False,
            "La sesión es inválida o ha expirado."
        )

    tipo_cuenta = payload.get("tipo_cuenta")

    # =================================================
    # VALIDAR CLIENTE
    # =================================================

    if tipo_cuenta == "cliente":

        id_usuario = payload.get("id_usuario")

        if not id_usuario:
            return respuesta(
                False,
                "El token no contiene un cliente válido."
            )

        usuario = user_repository.obtener_usuario_por_id(
            id_usuario
        )

        if not usuario:
            return respuesta(
                False,
                "El cliente de la sesión no existe."
            )

        correo_verificado = _obtener_campo(
            usuario,
            "correo_verificado",
            "CORREO_VERIFICADO"
        )

        estado = _obtener_campo(
            usuario,
            "estado",
            "ESTADO"
        )

        if not bool(correo_verificado):
            return respuesta(
                False,
                "El correo electrónico no está verificado."
            )

        if estado != 1:
            return respuesta(
                False,
                "La cuenta no está activa."
            )

        datos_cuenta = {
            "id_usuario": _obtener_campo(
                usuario, "id_usuario", "Id_USUARIO"
            ),
            "id_establecimiento": _obtener_campo(
                usuario, "id_establecimiento", "Id_ESTABLECIMIENTO"
            ),
            "nombre": _obtener_campo(
                usuario, "nombre", "NOMBRE"
            ),
            "correo": _obtener_campo(
                usuario, "correo", "CORREO"
            ),
            "telefono": _obtener_campo(
                usuario, "telefono", "TELEFONO"
            ),
            "cargo": "cliente",
            "estado": estado,
            "correo_verificado": True
        }

        return respuesta(
            True,
            "Sesión válida.",
            data={
                "tipo_cuenta": "cliente",
                "usuario": datos_cuenta,
                "establecimiento": None,
                "payload": payload
            }
        )

    # =================================================
    # VALIDAR ESTABLECIMIENTO
    # =================================================

    elif tipo_cuenta == "establecimiento":

        id_establecimiento = payload.get(
            "id_establecimiento"
        )

        if not id_establecimiento:
            return respuesta(
                False,
                "El token no contiene un establecimiento válido."
            )

        establecimiento = (
            user_repository.obtener_establecimiento_por_id(
                id_establecimiento
            )
        )

        if not establecimiento:
            return respuesta(
                False,
                "El establecimiento de la sesión no existe."
            )

        correo_verificado = _obtener_campo(
            establecimiento,
            "correo_verificado",
            "CORREO_VERIFICADO"
        )

        estado = _obtener_campo(
            establecimiento,
            "estado",
            "ESTADO"
        )

        if not bool(correo_verificado):
            return respuesta(
                False,
                "El correo electrónico no está verificado."
            )

        if estado != 1:
            return respuesta(
                False,
                "La cuenta no está activa."
            )

        datos_cuenta = {
            "id_establecimiento": _obtener_campo(
                establecimiento,
                "id_establecimiento",
                "Id_ESTABLECIMIENTO"
            ),
            "nombre_comercial": _obtener_campo(
                establecimiento,
                "nombre_comercial",
                "NOMBRE_COMERCIAL"
            ),
            "nombre": _obtener_campo(
                establecimiento, "nombre", "NOMBRE"
            ),
            "apellido": _obtener_campo(
                establecimiento, "apellido", "APELLIDO"
            ),
            "telefono": _obtener_campo(
                establecimiento, "telefono", "TELEFONO"
            ),
            "email": _obtener_campo(
                establecimiento, "email", "EMAIL"
            ),
            "direccion": _obtener_campo(
                establecimiento, "direccion", "DIRECCION"
            ),
            "estado": estado,
            "correo_verificado": True
        }

        return respuesta(
            True,
            "Sesión válida.",
            data={
                "tipo_cuenta": "establecimiento",
                "usuario": datos_cuenta,
                "establecimiento": datos_cuenta,
                "payload": payload
            }
        )

    # =================================================
    # TIPO DE CUENTA NO RECONOCIDO
    # =================================================

    return respuesta(
        False,
        "El tipo de cuenta de la sesión no es válido."
    )
