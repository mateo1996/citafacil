
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# LISTAR CLIENTES DE UN ESTABLECIMIENTO
# =====================================================

def obtener_todos_los_clientes(id_establecimiento):
    """Obtiene los clientes de un establecimiento específico."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_CLIENTE AS id_cliente,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                TELEFONO AS telefono,
                CORREO AS correo
            FROM CLIENTE
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
# OBTENER CLIENTE POR ID
# =====================================================

def obtener_cliente_por_id(id_cliente, id_establecimiento):
    """Obtiene un cliente verificando que pertenezca al establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_CLIENTE AS id_cliente,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                TELEFONO AS telefono,
                CORREO AS correo
            FROM CLIENTE
            WHERE Id_CLIENTE = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (id_cliente, id_establecimiento)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER CLIENTE POR TELÉFONO
# =====================================================

def obtener_cliente_por_telefono(telefono, id_establecimiento):
    """
    Busca un cliente por teléfono dentro de un establecimiento.

    El mismo teléfono puede existir en establecimientos diferentes.
    """

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_CLIENTE AS id_cliente,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                NOMBRE AS nombre,
                TELEFONO AS telefono,
                CORREO AS correo
            FROM CLIENTE
            WHERE TELEFONO = %s
              AND Id_ESTABLECIMIENTO = %s
            LIMIT 1
        """

        cursor.execute(
            consulta,
            (telefono, id_establecimiento)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# REGISTRAR CLIENTE
# =====================================================

def crear_cliente(
    id_establecimiento,
    nombre,
    telefono,
    correo=None
):
    """Registra un cliente asociado a un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO CLIENTE (
                Id_ESTABLECIMIENTO,
                NOMBRE,
                TELEFONO,
                CORREO
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            consulta,
            (
                id_establecimiento,
                nombre,
                telefono,
                correo
            )
        )

        id_cliente = cursor.lastrowid

        conexion.commit()

        return id_cliente

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR CLIENTE
# =====================================================

def actualizar_cliente(
    id_cliente,
    id_establecimiento,
    nombre,
    telefono,
    correo=None
):
    """Actualiza un cliente perteneciente al establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE CLIENTE
            SET
                NOMBRE = %s,
                TELEFONO = %s,
                CORREO = %s
            WHERE Id_CLIENTE = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                nombre,
                telefono,
                correo,
                id_cliente,
                id_establecimiento
            )
        )

        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ELIMINAR CLIENTE
# =====================================================

def eliminar_cliente(id_cliente, id_establecimiento):
    """Elimina un cliente verificando su establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            DELETE FROM CLIENTE
            WHERE Id_CLIENTE = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (id_cliente, id_establecimiento)
        )

        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()
