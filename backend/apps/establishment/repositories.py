
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# OBTENER ESTABLECIMIENTO POR ID
# =====================================================

def obtener_establecimiento_por_id(id_establecimiento):
    """Obtiene un establecimiento mediante su identificador."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

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
                WHATSAPP_PHONE_NUMBER_ID AS whatsapp_phone_number_id,
                CORREO_VERIFICADO AS correo_verificado,
                ESTADO AS estado
            FROM ESTABLECIMIENTO
            WHERE Id_ESTABLECIMIENTO = %s
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
    """Busca un establecimiento mediante su correo electrónico."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

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
        """

        cursor.execute(consulta, (email,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CREAR ESTABLECIMIENTO
# =====================================================

def crear_establecimiento(
    nombre_comercial,
    nombre,
    apellido,
    telefono,
    email,
    direccion,
    contrasena_hash
):
    """
    Crea una cuenta de establecimiento.

    El nombre de la función se conserva temporalmente
    para no romper el servicio que la utiliza.
    Ya no crea registros en la tabla USUARIO.
    """

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        conexion.start_transaction()

        cursor = conexion.cursor()

        consulta = """
            INSERT INTO ESTABLECIMIENTO (
                NOMBRE_COMERCIAL,
                NOMBRE,
                APELLIDO,
                TELEFONO,
                EMAIL,
                DIRECCION,
                CONTRASENA,
                CORREO_VERIFICADO,
                ESTADO
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0)
        """

        cursor.execute(
            consulta,
            (
                nombre_comercial,
                nombre,
                apellido,
                telefono,
                email,
                direccion,
                contrasena_hash
            )
        )

        id_establecimiento = cursor.lastrowid

        if not id_establecimiento:
            raise Exception(
                "No fue posible crear el establecimiento."
            )

        conexion.commit()

        return {
            "id_establecimiento": id_establecimiento
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()

# =====================================================
# OBTENER ESTABLECIMIENTO POR WHATSAPP PHONE NUMBER ID
# =====================================================

def obtener_establecimiento_por_whatsapp_phone_id(
    phone_number_id
):
    """
    Busca el establecimiento asociado a un número
    de WhatsApp Business Platform.
    """

    if not phone_number_id:
        return None

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE_COMERCIAL AS nombre_comercial,
                TELEFONO AS telefono,
                EMAIL AS email,
                ESTADO AS estado
            FROM ESTABLECIMIENTO
            WHERE WHATSAPP_PHONE_NUMBER_ID = %s
            LIMIT 1
        """

        cursor.execute(
            consulta,
            (phone_number_id,)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()
        


# =====================================================
# VINCULAR WHATSAPP A ESTABLECIMIENTO
# =====================================================

def vincular_whatsapp_establecimiento(
    id_establecimiento,
    phone_number_id
):
    """
    Guarda el identificador de WhatsApp Business
    en el establecimiento correspondiente.
    """

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:
        conexion.start_transaction()

        cursor = conexion.cursor()

        consulta = """
            UPDATE ESTABLECIMIENTO
            SET WHATSAPP_PHONE_NUMBER_ID = %s
            WHERE Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                phone_number_id,
                id_establecimiento
            )
        )

        if cursor.rowcount == 0:
            # Comprobar si el establecimiento existe
            cursor.execute(
                """
                SELECT Id_ESTABLECIMIENTO
                FROM ESTABLECIMIENTO
                WHERE Id_ESTABLECIMIENTO = %s
                """,
                (id_establecimiento,)
            )

            if not cursor.fetchone():
                raise ValueError(
                    "Establecimiento no encontrado."
                )

        conexion.commit()

        return True

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()



# =====================================================
# LISTAR ESTABLECIMIENTOS DISPONIBLES PARA CLIENTES
# =====================================================

def listar_establecimientos_disponibles():
    """Obtiene establecimientos activos y verificados."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE_COMERCIAL AS nombre_comercial,
                DIRECCION AS direccion
            FROM ESTABLECIMIENTO
            WHERE ESTADO = 1
              AND CORREO_VERIFICADO = 1
            ORDER BY NOMBRE_COMERCIAL ASC
        """

        cursor.execute(consulta)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()
