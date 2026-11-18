
import logging
import mysql.connector

from mysql.connector import Error
from config import settings


logger = logging.getLogger(__name__)


# =====================================================
# OBTENER CONEXIÓN CON MYSQL
# =====================================================

def obtener_conexion():
    """
    Establece y devuelve una conexión con MySQL.

    Retorna:
        - Conexión MySQL si se establece correctamente.
        - None si ocurre un error.
    """

    try:
        conexion = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            connection_timeout=10
        )

        if conexion.is_connected():
            return conexion

        try:
            conexion.close()
        except Error:
            logger.exception(
                "Error al cerrar una conexión MySQL no válida."
            )

    except Error:
        logger.exception(
            "Error al establecer la conexión con MySQL."
        )

    return None


# =====================================================
# VERIFICAR CONEXIÓN CON MYSQL
# =====================================================

def verificar_conexion():
    """
    Comprueba si es posible establecer una conexión con MySQL.

    Retorna:
        - True si la conexión funciona.
        - False si no se puede conectar.
    """

    conexion = obtener_conexion()

    if conexion is None:
        return False

    try:
        return conexion.is_connected()

    except Error:
        logger.exception(
            "Error al verificar la conexión con MySQL."
        )

        return False

    finally:
        conexion.close()
