
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# LISTAR SERVICIOS DE UN ESTABLECIMIENTO
# =====================================================

def obtener_servicios_por_establecimiento(id_establecimiento):
    """Obtiene todos los servicios de un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_SERVICIO AS id_servicio,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                DESCRIPCION AS descripcion,
                DURACION_MINUTOS AS duracion_minutos,
                PRECIO AS precio,
                ESTADO AS estado
            FROM SERVICIO
            WHERE Id_ESTABLECIMIENTO = %s
            ORDER BY NOMBRE ASC
        """

        cursor.execute(consulta, (id_establecimiento,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER SERVICIO POR ID
# =====================================================

def obtener_servicio_por_id(id_servicio, id_establecimiento):
    """Obtiene un servicio perteneciente a un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_SERVICIO AS id_servicio,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                DESCRIPCION AS descripcion,
                DURACION_MINUTOS AS duracion_minutos,
                PRECIO AS precio,
                ESTADO AS estado
            FROM SERVICIO
            WHERE Id_SERVICIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (id_servicio, id_establecimiento)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CREAR SERVICIO
# =====================================================

def crear_servicio(
    id_establecimiento,
    nombre,
    descripcion,
    duracion_minutos,
    precio
):
    """Registra un nuevo servicio."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO SERVICIO (
                Id_ESTABLECIMIENTO,
                NOMBRE,
                DESCRIPCION,
                DURACION_MINUTOS,
                PRECIO,
                ESTADO
            )
            VALUES (%s, %s, %s, %s, %s, 1)
        """

        cursor.execute(
            consulta,
            (
                id_establecimiento,
                nombre,
                descripcion,
                duracion_minutos,
                precio
            )
        )

        id_servicio = cursor.lastrowid

        conexion.commit()

        return id_servicio

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR SERVICIO
# =====================================================

def actualizar_servicio(
    id_servicio,
    id_establecimiento,
    nombre,
    descripcion,
    duracion_minutos,
    precio
):
    """Actualiza los datos de un servicio."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE SERVICIO
            SET
                NOMBRE = %s,
                DESCRIPCION = %s,
                DURACION_MINUTOS = %s,
                PRECIO = %s
            WHERE Id_SERVICIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                nombre,
                descripcion,
                duracion_minutos,
                precio,
                id_servicio,
                id_establecimiento
            )
        )

        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CAMBIAR ESTADO DEL SERVICIO
# =====================================================

def actualizar_estado_servicio(
    id_servicio,
    id_establecimiento,
    estado
):
    """Activa o desactiva un servicio."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE SERVICIO
            SET ESTADO = %s
            WHERE Id_SERVICIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                estado,
                id_servicio,
                id_establecimiento
            )
        )

        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()
        
        

# =====================================================
# LISTAR SERVICIOS ACTIVOS PARA CLIENTES
# =====================================================

def obtener_servicios_activos_por_establecimiento(
    id_establecimiento
):
    """Obtiene únicamente los servicios activos."""

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
                Id_SERVICIO AS id_servicio,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                DESCRIPCION AS descripcion,
                DURACION_MINUTOS AS duracion_minutos,
                PRECIO AS precio
            FROM SERVICIO
            WHERE Id_ESTABLECIMIENTO = %s
              AND ESTADO = 1
            ORDER BY NOMBRE ASC
        """

        cursor.execute(
            consulta,
            (id_establecimiento,)
        )

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()

