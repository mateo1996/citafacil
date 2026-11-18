
import hashlib
from datetime import datetime, timezone

from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# CONSTANTES
# =====================================================

TIPOS_TOKEN_PERMITIDOS = (
    "verificacion_email",
    "recuperacion_password"
)


# =====================================================
# UTILIDADES INTERNAS
# =====================================================

def _validar_tipo_token(tipo: str):
    if tipo not in TIPOS_TOKEN_PERMITIDOS:
        raise ValueError("El tipo de token no es válido.")


def _validar_propietario(id_usuario, id_establecimiento):
    """
    Cada token debe pertenecer exactamente a un usuario
    o a un establecimiento.
    """

    tiene_usuario = id_usuario is not None
    tiene_establecimiento = id_establecimiento is not None

    if tiene_usuario == tiene_establecimiento:
        raise ValueError(
            "El token debe pertenecer a un usuario "
            "o a un establecimiento, pero no a ambos."
        )


def _obtener_hash_token(token: str) -> str:
    if not isinstance(token, str) or not token:
        raise ValueError("El token no es válido.")

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalizar_fecha_utc(fecha: datetime) -> datetime:
    if not isinstance(fecha, datetime):
        raise ValueError("La fecha de expiración no es válida.")

    if fecha.tzinfo is None:
        return fecha

    return fecha.astimezone(timezone.utc).replace(tzinfo=None)


# =====================================================
# GUARDAR TOKEN
# =====================================================

def guardar_token(
    id_usuario,
    token: str,
    tipo: str,
    expira_en: datetime,
    id_establecimiento=None
) -> int:

    _validar_tipo_token(tipo)

    _validar_propietario(
        id_usuario,
        id_establecimiento
    )

    token_hash = _obtener_hash_token(token)
    fecha_expiracion = _normalizar_fecha_utc(expira_en)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO TOKEN_AUTENTICACION (
                ID_USUARIO,
                ID_ESTABLECIMIENTO,
                TOKEN_HASH,
                TIPO,
                EXPIRA_EN
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            consulta,
            (
                id_usuario,
                id_establecimiento,
                token_hash,
                tipo,
                fecha_expiracion
            )
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER TOKEN VÁLIDO
# =====================================================

def obtener_token_valido(token: str, tipo: str):

    _validar_tipo_token(tipo)

    token_hash = _obtener_hash_token(token)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                ID_TOKEN,
                ID_USUARIO,
                ID_ESTABLECIMIENTO,
                TIPO,
                EXPIRA_EN,
                USADO_EN
            FROM TOKEN_AUTENTICACION
            WHERE TOKEN_HASH = %s
              AND TIPO = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
            LIMIT 1
        """

        cursor.execute(consulta, (token_hash, tipo))

        registro = cursor.fetchone()

        if registro:
            try:
                _validar_propietario(
                    registro["ID_USUARIO"],
                    registro["ID_ESTABLECIMIENTO"]
                )
            except ValueError:
                return None

        return registro

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CONSUMIR TOKEN DE FORMA ATÓMICA
# =====================================================

def consumir_token(token: str, tipo: str):

    _validar_tipo_token(tipo)

    token_hash = _obtener_hash_token(token)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        conexion.start_transaction()

        cursor = conexion.cursor(dictionary=True)

        consulta_busqueda = """
            SELECT
                ID_TOKEN,
                ID_USUARIO,
                ID_ESTABLECIMIENTO,
                TIPO,
                EXPIRA_EN,
                USADO_EN
            FROM TOKEN_AUTENTICACION
            WHERE TOKEN_HASH = %s
              AND TIPO = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
            LIMIT 1
            FOR UPDATE
        """

        cursor.execute(
            consulta_busqueda,
            (token_hash, tipo)
        )

        registro_token = cursor.fetchone()

        if not registro_token:
            conexion.rollback()
            return None

        try:
            _validar_propietario(
                registro_token["ID_USUARIO"],
                registro_token["ID_ESTABLECIMIENTO"]
            )
        except ValueError:
            conexion.rollback()
            return None

        consulta_actualizacion = """
            UPDATE TOKEN_AUTENTICACION
            SET USADO_EN = UTC_TIMESTAMP()
            WHERE ID_TOKEN = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
        """

        cursor.execute(
            consulta_actualizacion,
            (registro_token["ID_TOKEN"],)
        )

        if cursor.rowcount != 1:
            conexion.rollback()
            return None

        conexion.commit()

        return registro_token

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CONSUMIR TOKEN Y VERIFICAR CORREO ATÓMICAMENTE
# =====================================================

def consumir_token_verificacion(token: str):

    tipo = "verificacion_email"

    _validar_tipo_token(tipo)

    token_hash = _obtener_hash_token(token)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        conexion.start_transaction()

        cursor = conexion.cursor(dictionary=True)

        # ---------------------------------------------
        # BUSCAR Y BLOQUEAR EL TOKEN
        # ---------------------------------------------

        consulta_token = """
            SELECT
                ID_TOKEN,
                ID_USUARIO,
                ID_ESTABLECIMIENTO
            FROM TOKEN_AUTENTICACION
            WHERE TOKEN_HASH = %s
              AND TIPO = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
            LIMIT 1
            FOR UPDATE
        """

        cursor.execute(
            consulta_token,
            (token_hash, tipo)
        )

        registro_token = cursor.fetchone()

        if not registro_token:
            conexion.rollback()
            return None

        id_usuario = registro_token["ID_USUARIO"]
        id_establecimiento = registro_token["ID_ESTABLECIMIENTO"]

        try:
            _validar_propietario(
                id_usuario,
                id_establecimiento
            )
        except ValueError:
            conexion.rollback()
            return None

        # ---------------------------------------------
        # VERIFICAR CLIENTE
        # ---------------------------------------------

        if id_usuario is not None:

            cursor.execute(
                """
                SELECT Id_USUARIO, CORREO_VERIFICADO
                FROM USUARIO
                WHERE Id_USUARIO = %s
                LIMIT 1
                FOR UPDATE
                """,
                (id_usuario,)
            )

            entidad = cursor.fetchone()

            if not entidad or entidad["CORREO_VERIFICADO"]:
                conexion.rollback()
                return None

            cursor.execute(
                """
                UPDATE USUARIO
                SET
                    CORREO_VERIFICADO = 1,
                    ESTADO = 1
                WHERE Id_USUARIO = %s
                  AND CORREO_VERIFICADO = 0
                """,
                (id_usuario,)
            )

        # ---------------------------------------------
        # VERIFICAR ESTABLECIMIENTO
        # ---------------------------------------------

        else:

            cursor.execute(
                """
                SELECT
                    Id_ESTABLECIMIENTO,
                    CORREO_VERIFICADO
                FROM ESTABLECIMIENTO
                WHERE Id_ESTABLECIMIENTO = %s
                LIMIT 1
                FOR UPDATE
                """,
                (id_establecimiento,)
            )

            entidad = cursor.fetchone()

            if not entidad or entidad["CORREO_VERIFICADO"]:
                conexion.rollback()
                return None

            cursor.execute(
                """
                UPDATE ESTABLECIMIENTO
                SET
                    CORREO_VERIFICADO = 1,
                    ESTADO = 1
                WHERE Id_ESTABLECIMIENTO = %s
                  AND CORREO_VERIFICADO = 0
                """,
                (id_establecimiento,)
            )

        if cursor.rowcount != 1:
            conexion.rollback()
            return None

        # ---------------------------------------------
        # MARCAR TOKEN COMO UTILIZADO
        # ---------------------------------------------

        cursor.execute(
            """
            UPDATE TOKEN_AUTENTICACION
            SET USADO_EN = UTC_TIMESTAMP()
            WHERE ID_TOKEN = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
            """,
            (registro_token["ID_TOKEN"],)
        )

        if cursor.rowcount != 1:
            conexion.rollback()
            return None

        conexion.commit()

        return {
            "id_usuario": id_usuario,
            "id_establecimiento": id_establecimiento,
            "id_token": registro_token["ID_TOKEN"]
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# MARCAR TOKEN COMO UTILIZADO
# =====================================================

def marcar_token_como_usado(id_token: int) -> bool:

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE TOKEN_AUTENTICACION
            SET USADO_EN = UTC_TIMESTAMP()
            WHERE ID_TOKEN = %s
              AND USADO_EN IS NULL
              AND EXPIRA_EN > UTC_TIMESTAMP()
        """

        cursor.execute(consulta, (id_token,))

        conexion.commit()

        return cursor.rowcount == 1

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# INVALIDAR TOKENS DE UN USUARIO
# =====================================================

def invalidar_tokens_usuario(id_usuario: int, tipo: str) -> int:

    _validar_tipo_token(tipo)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE TOKEN_AUTENTICACION
            SET USADO_EN = UTC_TIMESTAMP()
            WHERE ID_USUARIO = %s
              AND ID_ESTABLECIMIENTO IS NULL
              AND TIPO = %s
              AND USADO_EN IS NULL
        """

        cursor.execute(consulta, (id_usuario, tipo))

        conexion.commit()

        return cursor.rowcount

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# INVALIDAR TOKENS DE UN ESTABLECIMIENTO
# =====================================================

def invalidar_tokens_establecimiento(
    id_establecimiento: int,
    tipo: str
) -> int:

    _validar_tipo_token(tipo)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE TOKEN_AUTENTICACION
            SET USADO_EN = UTC_TIMESTAMP()
            WHERE ID_ESTABLECIMIENTO = %s
              AND ID_USUARIO IS NULL
              AND TIPO = %s
              AND USADO_EN IS NULL
        """

        cursor.execute(
            consulta,
            (id_establecimiento, tipo)
        )

        conexion.commit()

        return cursor.rowcount

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()
