
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# OBTENER ESTABLECIMIENTO POR ID
# =====================================================

def obtener_establecimiento_por_id(id_establecimiento):
    """Obtiene los datos de un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE_COMERCIAL AS nombre_comercial,
                NOMBRE AS nombre,
                APELLIDO AS apellido,
                TELEFONO AS telefono,
                EMAIL AS email,
                DIRECCION AS direccion,
                CORREO_VERIFICADO AS correo_verificado,
                ESTADO AS estado
            FROM ESTABLECIMIENTO
            WHERE Id_ESTABLECIMIENTO = %s
            LIMIT 1
        """

        cursor.execute(consulta, (id_establecimiento,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER ESTABLECIMIENTO POR CORREO
# =====================================================

def obtener_establecimiento_por_correo(email):
    """Obtiene un establecimiento mediante su correo."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE_COMERCIAL AS nombre_comercial,
                NOMBRE AS nombre,
                APELLIDO AS apellido,
                TELEFONO AS telefono,
                EMAIL AS email,
                DIRECCION AS direccion,
                CONTRASENA AS contrasena,
                CORREO_VERIFICADO AS correo_verificado,
                ESTADO AS estado
            FROM ESTABLECIMIENTO
            WHERE EMAIL = %s
            LIMIT 1
        """

        cursor.execute(consulta, (email,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER CLIENTE POR CORREO
# =====================================================

def obtener_usuario_por_correo(correo):
    """Obtiene un cliente mediante su correo electrónico."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_USUARIO AS id_usuario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                CORREO AS correo,
                TELEFONO AS telefono,
                `CONTRASEÑA` AS contrasena,
                CARGO AS cargo,
                ESTADO AS estado,
                CORREO_VERIFICADO AS correo_verificado
            FROM USUARIO
            WHERE CORREO = %s
            LIMIT 1
        """

        cursor.execute(consulta, (correo,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER CLIENTE POR ID
# =====================================================

def obtener_usuario_por_id(id_usuario):
    """Obtiene un cliente mediante su identificador."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_USUARIO AS id_usuario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                CORREO AS correo,
                TELEFONO AS telefono,
                `CONTRASEÑA` AS contrasena,
                CARGO AS cargo,
                ESTADO AS estado,
                CORREO_VERIFICADO AS correo_verificado
            FROM USUARIO
            WHERE Id_USUARIO = %s
            LIMIT 1
        """

        cursor.execute(consulta, (id_usuario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR CONTRASEÑA DE CLIENTE
# =====================================================

def actualizar_contrasena(id_usuario, nueva_contrasena_hash):
    """Actualiza la contraseña de un cliente."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE USUARIO
            SET `CONTRASEÑA` = %s
            WHERE Id_USUARIO = %s
        """

        cursor.execute(
            consulta,
            (nueva_contrasena_hash, id_usuario)
        )

        if cursor.rowcount > 0:
            conexion.commit()
            return True

        cursor.execute(
            """
            SELECT 1
            FROM USUARIO
            WHERE Id_USUARIO = %s
            LIMIT 1
            """,
            (id_usuario,)
        )

        usuario_existe = cursor.fetchone() is not None

        if usuario_existe:
            conexion.commit()
            return True

        conexion.rollback()
        return False

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR CONTRASEÑA DE ESTABLECIMIENTO
# =====================================================

def actualizar_contrasena_establecimiento(
    id_establecimiento,
    nueva_contrasena_hash
):
    """Actualiza la contraseña de un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE ESTABLECIMIENTO
            SET CONTRASENA = %s
            WHERE Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (nueva_contrasena_hash, id_establecimiento)
        )

        if cursor.rowcount > 0:
            conexion.commit()
            return True

        cursor.execute(
            """
            SELECT 1
            FROM ESTABLECIMIENTO
            WHERE Id_ESTABLECIMIENTO = %s
            LIMIT 1
            """,
            (id_establecimiento,)
        )

        establecimiento_existe = cursor.fetchone() is not None

        if establecimiento_existe:
            conexion.commit()
            return True

        conexion.rollback()
        return False

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()

# =====================================================
# CREAR CLIENTE
# =====================================================

def crear_usuario(
    id_establecimiento,
    nombre,
    correo,
    telefono,
    contrasena_hash,
    cargo,
    estado
):
    """Crea un cliente independiente en la base de datos."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO USUARIO (
                Id_ESTABLECIMIENTO,
                NOMBRE,
                CORREO,
                TELEFONO,
                `CONTRASEÑA`,
                CARGO,
                ESTADO,
                CORREO_VERIFICADO
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            consulta,
            (
                id_establecimiento,
                nombre,
                correo,
                telefono,
                contrasena_hash,
                cargo,
                estado,
                0
            )
        )

        id_usuario = cursor.lastrowid

        if not id_usuario:
            raise Exception("No fue posible crear el cliente.")

        conexion.commit()

        return id_usuario

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()



# =====================================================
# LISTAR CLIENTES POR ESTABLECIMIENTO
# =====================================================

def listar_usuarios_por_establecimiento(id_establecimiento):
    """Lista los clientes asociados a un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_USUARIO AS id_usuario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                CORREO AS correo,
                TELEFONO AS telefono,
                CARGO AS cargo,
                ESTADO AS estado,
                CORREO_VERIFICADO AS correo_verificado
            FROM USUARIO
            WHERE Id_ESTABLECIMIENTO = %s
            ORDER BY Id_USUARIO DESC
        """

        cursor.execute(consulta, (id_establecimiento,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR CLIENTE
# =====================================================

def actualizar_usuario(
    id_usuario,
    nombre,
    correo,
    telefono,
    cargo
):
    """Actualiza los datos básicos de un cliente."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE USUARIO
            SET
                NOMBRE = %s,
                CORREO = %s,
                TELEFONO = %s
            WHERE Id_USUARIO = %s
        """

        cursor.execute(
            consulta,
            (
                nombre,
                correo,
                telefono,
                id_usuario
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CAMBIAR ESTADO DE CLIENTE
# =====================================================

def cambiar_estado_usuario(id_usuario, nuevo_estado):
    """Activa o desactiva un cliente."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE USUARIO
            SET ESTADO = %s
            WHERE Id_USUARIO = %s
        """

        cursor.execute(
            consulta,
            (nuevo_estado, id_usuario)
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()
