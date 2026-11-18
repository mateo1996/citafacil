
from apps.user import repositories
from apps.user import serializers

from infrastructure.security.password import hash_password

from apps.authentication import services as authentication_services


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
# REGISTRAR CLIENTE
# =====================================================

def registrar_usuario(datos, id_establecimiento=None):
    """Registra un cliente independiente y envía su verificación."""

    if not isinstance(datos, dict):
        return respuesta(
            False,
            "Los datos del registro no son válidos."
        )

    datos = dict(datos)

    # ---------------------------------------------
    # DEFINIR TIPO DE CUENTA
    # ---------------------------------------------

    datos["cargo"] = "cliente"

    # ---------------------------------------------
    # NORMALIZAR CORREO
    # ---------------------------------------------

    correo = datos.get("correo")

    if isinstance(correo, str):
        datos["correo"] = correo.strip().lower()

    # ---------------------------------------------
    # VALIDAR DATOS
    # ---------------------------------------------

    errores = serializers.validar_datos_registro(datos)

    if errores:
        return respuesta(
            False,
            "Los datos del registro no son válidos.",
            errores=errores
        )

    correo = datos["correo"]

    # ---------------------------------------------
    # COMPROBAR CORREO EN CLIENTES
    # ---------------------------------------------

    usuario_existente = repositories.obtener_usuario_por_correo(
        correo
    )

    if usuario_existente:
        return respuesta(
            False,
            "El correo electrónico ya está registrado.",
            errores={
                "correo": "Este correo ya está en uso."
            }
        )

    # ---------------------------------------------
    # COMPROBAR CORREO EN ESTABLECIMIENTOS
    # ---------------------------------------------

    establecimiento_existente = (
        repositories.obtener_establecimiento_por_correo(correo)
    )

    if establecimiento_existente:
        return respuesta(
            False,
            "El correo electrónico ya está registrado.",
            errores={
                "correo": "Este correo ya está asociado a una cuenta."
            }
        )

    # ---------------------------------------------
    # CIFRAR CONTRASEÑA
    # ---------------------------------------------

    try:
        contrasena_hash = hash_password(
            datos["contrasena"]
        )

    except Exception:
        return respuesta(
            False,
            "No fue posible procesar la contraseña."
        )

    # ---------------------------------------------
    # CREAR CLIENTE
    # ---------------------------------------------

    try:
        id_usuario = repositories.crear_usuario(
            id_establecimiento=None,
            nombre=datos["nombre"].strip(),
            correo=correo,
            telefono=datos.get("telefono", "").strip() or None,
            contrasena_hash=contrasena_hash,
            cargo="cliente",
            estado="inactivo"
        )

    except Exception:
        return respuesta(
            False,
            "No fue posible registrar el cliente."
        )

    if not id_usuario:
        return respuesta(
            False,
            "No fue posible registrar el cliente."
        )

    # ---------------------------------------------
    # ENVIAR VERIFICACIÓN
    # ---------------------------------------------

    correo_enviado = (
        authentication_services.enviar_verificacion_correo(
            id_usuario=id_usuario,
            correo=correo,
            nombre=datos["nombre"].strip()
        )
    )

    # ---------------------------------------------
    # RESPUESTA FINAL
    # ---------------------------------------------

    if not correo_enviado:
        return respuesta(
            True,
            "Cliente registrado, pero no fue posible enviar "
            "el correo de verificación. Solicita un nuevo envío.",
            data={
                "id_usuario": id_usuario,
                "tipo_cuenta": "cliente",
                "correo_verificado": False
            }
        )

    return respuesta(
        True,
        "Cliente registrado. Revisa tu correo para verificar la cuenta.",
        data={
            "id_usuario": id_usuario,
            "tipo_cuenta": "cliente",
            "correo_verificado": False
        }
    )



# =====================================================
# OBTENER USUARIO POR ID
# =====================================================

def obtener_usuario(id_usuario):
    """Obtiene la información de un usuario."""

    usuario = repositories.obtener_usuario_por_id(id_usuario)

    if not usuario:
        return respuesta(
            False,
            "Usuario no encontrado."
        )

    return respuesta(
        True,
        "Usuario encontrado.",
        data=serializers.serializar_usuario(usuario)
    )


# =====================================================
# LISTAR USUARIOS
# =====================================================

def listar_usuarios(id_establecimiento):
    """Lista los usuarios pertenecientes a un establecimiento."""

    usuarios = repositories.listar_usuarios_por_establecimiento(
        id_establecimiento
    )

    return respuesta(
        True,
        "Usuarios obtenidos correctamente.",
        data=serializers.serializar_usuarios(usuarios)
    )



# =====================================================
# ACTUALIZAR CLIENTE
# =====================================================

def actualizar_usuario(id_usuario, datos):
    """Actualiza los datos permitidos de un cliente."""

    if not isinstance(datos, dict) or not datos:
        return respuesta(
            False,
            "Debes proporcionar datos para actualizar."
        )

    campos_permitidos = {
        "nombre",
        "correo",
        "telefono"
    }

    campos_no_permitidos = set(datos.keys()) - campos_permitidos

    if campos_no_permitidos:
        return respuesta(
            False,
            "Se han enviado campos que no pueden modificarse.",
            errores={
                campo: "Este campo no está permitido."
                for campo in campos_no_permitidos
            }
        )

    usuario = repositories.obtener_usuario_por_id(id_usuario)

    if not usuario:
        return respuesta(
            False,
            "Usuario no encontrado."
        )

    datos_actualizados = {
        "nombre": usuario.get("nombre"),
        "correo": usuario.get("correo"),
        "telefono": usuario.get("telefono")
    }

    datos_actualizados.update(datos)

    if isinstance(datos_actualizados["correo"], str):
        datos_actualizados["correo"] = (
            datos_actualizados["correo"].strip().lower()
        )

    errores = serializers.validar_datos_actualizacion(
        datos_actualizados
    )

    if errores:
        return respuesta(
            False,
            "Los datos de actualización no son válidos.",
            errores=errores
        )

    correo_anterior = usuario.get("correo")
    correo_nuevo = datos_actualizados["correo"]

    if correo_nuevo != correo_anterior:

        otro_usuario = repositories.obtener_usuario_por_correo(
            correo_nuevo
        )

        if (
            otro_usuario
            and otro_usuario.get("id_usuario") != id_usuario
        ):
            return respuesta(
                False,
                "El correo electrónico ya está registrado.",
                errores={
                    "correo": "Este correo ya está en uso."
                }
            )

        establecimiento_existente = (
            repositories.obtener_establecimiento_por_correo(
                correo_nuevo
            )
        )

        if establecimiento_existente:
            return respuesta(
                False,
                "El correo electrónico ya está registrado.",
                errores={
                    "correo": "Este correo ya está asociado a otra cuenta."
                }
            )

    filas_afectadas = repositories.actualizar_usuario(
        id_usuario=id_usuario,
        nombre=datos_actualizados["nombre"].strip(),
        correo=correo_nuevo,
        telefono=(
            datos_actualizados["telefono"].strip()
            if datos_actualizados["telefono"]
            else None
        ),
        cargo=usuario.get("cargo")
    )

    if not filas_afectadas:
        return respuesta(
            False,
            "No fue posible actualizar el usuario."
        )

    if correo_nuevo != correo_anterior:

        correo_enviado = authentication_services.enviar_verificacion_correo(
            id_usuario=id_usuario,
            correo=correo_nuevo,
            nombre=datos_actualizados["nombre"].strip()
        )

        if not correo_enviado:
            return respuesta(
                True,
                "Los datos fueron actualizados, pero no fue posible "
                "enviar el nuevo correo de verificación.",
                data={
                    "correo_verificado": False
                }
            )

        return respuesta(
            True,
            "Correo actualizado. Debes verificar la nueva dirección.",
            data={
                "correo_verificado": False
            }
        )

    return respuesta(
        True,
        "Usuario actualizado correctamente."
    )



# =====================================================
# CAMBIAR ESTADO DE CLIENTE
# =====================================================

def cambiar_estado(id_usuario, nuevo_estado):
    """Activa o desactiva una cuenta de cliente."""

    estados_permitidos = {
        "activo": 1,
        "inactivo": 0
    }

    if nuevo_estado not in estados_permitidos:
        return respuesta(
            False,
            "El estado indicado no es válido."
        )

    usuario = repositories.obtener_usuario_por_id(id_usuario)

    if not usuario:
        return respuesta(
            False,
            "Cliente no encontrado."
        )

    estado_numerico = estados_permitidos[nuevo_estado]

    # No permitir activar cuentas sin correo verificado.
    if (
        estado_numerico == 1
        and not usuario.get("correo_verificado")
    ):
        return respuesta(
            False,
            "No se puede activar una cuenta cuyo correo "
            "electrónico no ha sido verificado."
        )

    filas_afectadas = repositories.cambiar_estado_usuario(
        id_usuario,
        estado_numerico
    )

    if not filas_afectadas:
        # Comprobar si el usuario existe y ya tenía ese estado.
        usuario_actualizado = repositories.obtener_usuario_por_id(
            id_usuario
        )

        if (
            not usuario_actualizado
            or usuario_actualizado.get("estado") != estado_numerico
        ):
            return respuesta(
                False,
                "No se pudo actualizar el estado del cliente."
            )

    return respuesta(
        True,
        "Estado del cliente actualizado correctamente.",
        data={
            "estado": estado_numerico
        }
    )
