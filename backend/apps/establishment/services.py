
from apps.establishment import repositories
from apps.establishment import serializers

from apps.user import repositories as user_repository

from apps.authentication import services as authentication_services

from infrastructure.security.password import hash_password


# =====================================================
# RESPUESTAS ESTÁNDAR
# =====================================================

def respuesta(ok, mensaje, data=None, errores=None):
    """Estandariza las respuestas del servicio."""

    return {
        "ok": ok,
        "mensaje": mensaje,
        "data": data,
        "errores": errores or {}
    }


# =====================================================
# REGISTRAR ESTABLECIMIENTO
# =====================================================

def registrar_establecimiento(datos):
    """Registra una cuenta de establecimiento y solicita su verificación."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Los datos del establecimiento no son válidos."
        )

    datos = dict(datos)

    # ---------------------------------------------
    # NORMALIZAR DATOS
    # ---------------------------------------------

    campos_texto = (
        "nombre",
        "apellido",
        "nombre_establecimiento",
        "email",
        "direccion",
        "telefono"
    )

    for campo in campos_texto:
        valor = datos.get(campo)

        if isinstance(valor, str):
            datos[campo] = valor.strip()

    email = datos.get("email")

    if isinstance(email, str):
        datos["email"] = email.lower()

    # ---------------------------------------------
    # VALIDAR DATOS
    # ---------------------------------------------

    errores = serializers.validar_datos_establecimiento(datos)

    if errores:
        return respuesta(
            False,
            "Los datos del establecimiento no son válidos.",
            errores=errores
        )

    email = datos["email"]

    # ---------------------------------------------
    # COMPROBAR CORREO EN ESTABLECIMIENTOS
    # ---------------------------------------------

    establecimiento_existente = (
        repositories.obtener_establecimiento_por_correo(email)
    )

    if establecimiento_existente:
        return respuesta(
            False,
            "El correo electrónico ya pertenece a un establecimiento.",
            errores={
                "email": "Este correo ya está registrado."
            }
        )

    # ---------------------------------------------
    # COMPROBAR CORREO EN CLIENTES
    # ---------------------------------------------

    usuario_existente = (
        user_repository.obtener_usuario_por_correo(email)
    )

    if usuario_existente:
        return respuesta(
            False,
            "El correo electrónico ya está registrado.",
            errores={
                "email": "Este correo ya está asociado a una cuenta."
            }
        )

    # ---------------------------------------------
    # CIFRAR CONTRASEÑA
    # ---------------------------------------------

    try:
        contrasena_hash = hash_password(datos["contrasena"])

    except Exception:
        return respuesta(
            False,
            "No fue posible procesar la contraseña."
        )

    # ---------------------------------------------
    # CREAR ESTABLECIMIENTO
    # ---------------------------------------------

    try:
        resultado = repositories.crear_establecimiento(
            nombre_comercial=datos["nombre_establecimiento"],
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            telefono=datos.get("telefono") or None,
            email=email,
            direccion=datos["direccion"],
            contrasena_hash=contrasena_hash
        )

        id_establecimiento = resultado["id_establecimiento"]

    except Exception:
        return respuesta(
            False,
            "No fue posible registrar el establecimiento. "
            "Verifica los datos e inténtalo nuevamente."
        )

    # ---------------------------------------------
    # ENVIAR VERIFICACIÓN DE CORREO
    # ---------------------------------------------

    correo_enviado = (
        authentication_services.enviar_verificacion_correo(
            correo=email,
            nombre=f'{datos["nombre"]} {datos["apellido"]}',
            id_establecimiento=id_establecimiento
        )
    )

    # ---------------------------------------------
    # RESPUESTA FINAL
    # ---------------------------------------------

    if not correo_enviado:
        return respuesta(
            True,
            "El establecimiento fue registrado, pero no fue "
            "posible enviar el correo de verificación. "
            "Solicita el reenvío del correo.",
            data={
                "id_establecimiento": id_establecimiento,
                "tipo_cuenta": "establecimiento",
                "correo_verificacion_enviado": False
            }
        )

    return respuesta(
        True,
        "Establecimiento registrado correctamente. "
        "Revisa tu correo electrónico para verificar tu cuenta.",
        data={
            "id_establecimiento": id_establecimiento,
            "tipo_cuenta": "establecimiento",
            "correo_verificacion_enviado": True
        }
    )


# =====================================================
# OBTENER ESTABLECIMIENTO
# =====================================================

def obtener_establecimiento(id_establecimiento):
    """Obtiene un establecimiento mediante su identificador."""

    establecimiento = repositories.obtener_establecimiento_por_id(
        id_establecimiento
    )

    if not establecimiento:
        return respuesta(
            False,
            "Establecimiento no encontrado."
        )

    return respuesta(
        True,
        "Establecimiento obtenido correctamente.",
        data=serializers.serializar_establecimiento(establecimiento)
    )


# =====================================================
# CONSULTAR ESTABLECIMIENTO POR CORREO
# =====================================================

def obtener_establecimiento_por_correo(email):
    """Consulta si existe un establecimiento con determinado correo."""

    if not isinstance(email, str) or not email.strip():
        return respuesta(
            False,
            "Debes proporcionar un correo electrónico válido."
        )

    establecimiento = repositories.obtener_establecimiento_por_correo(
        email.strip().lower()
    )

    if not establecimiento:
        return respuesta(
            False,
            "Establecimiento no encontrado."
        )

    return respuesta(
        True,
        "Establecimiento obtenido correctamente.",
        data=serializers.serializar_establecimiento(establecimiento)
    )



# =====================================================
# VINCULAR NÚMERO DE WHATSAPP
# =====================================================

def vincular_whatsapp_establecimiento(
    id_establecimiento,
    phone_number_id
):
    """
    Asocia un número de WhatsApp Business Platform
    con un establecimiento.
    """

    # ---------------------------------------------
    # VALIDAR IDENTIFICADOR DEL ESTABLECIMIENTO
    # ---------------------------------------------

    if (
        not isinstance(id_establecimiento, int)
        or isinstance(id_establecimiento, bool)
        or id_establecimiento <= 0
    ):
        return respuesta(
            False,
            "El identificador del establecimiento no es válido."
        )

    # ---------------------------------------------
    # VALIDAR PHONE NUMBER ID
    # ---------------------------------------------

    if (
        not isinstance(phone_number_id, str)
        or not phone_number_id.strip()
    ):
        return respuesta(
            False,
            "El identificador de WhatsApp no es válido.",
            errores={
                "phone_number_id": (
                    "Debes proporcionar un identificador válido."
                )
            }
        )

    phone_number_id = phone_number_id.strip()

    if len(phone_number_id) > 50:
        return respuesta(
            False,
            "El identificador de WhatsApp supera la longitud permitida."
        )

    # ---------------------------------------------
    # COMPROBAR ESTABLECIMIENTO
    # ---------------------------------------------

    establecimiento = (
        repositories.obtener_establecimiento_por_id(
            id_establecimiento
        )
    )

    if not establecimiento:
        return respuesta(
            False,
            "Establecimiento no encontrado."
        )

    # ---------------------------------------------
    # VINCULAR NÚMERO
    # ---------------------------------------------

    try:

        repositories.vincular_whatsapp_establecimiento(
            id_establecimiento,
            phone_number_id
        )

        return respuesta(
            True,
            "Número de WhatsApp vinculado correctamente.",
            data={
                "id_establecimiento": id_establecimiento,
                "phone_number_id": phone_number_id
            }
        )

    except Exception:
        return respuesta(
            False,
            "No fue posible vincular el número de WhatsApp. "
            "Verifica que no esté asociado a otro establecimiento."
        )


# =====================================================
# LISTAR ESTABLECIMIENTOS PARA CLIENTES
# =====================================================

def listar_establecimientos_disponibles():
    """Lista establecimientos activos y verificados."""

    try:
        establecimientos = (
            repositories.listar_establecimientos_disponibles()
        )

        return respuesta(
            True,
            "Establecimientos disponibles obtenidos correctamente.",
            data=establecimientos
        )

    except Exception:
        return respuesta(
            False,
            "No fue posible obtener los establecimientos disponibles."
        )
