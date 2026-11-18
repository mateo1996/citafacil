
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# LISTAR HORARIOS DE UN ESTABLECIMIENTO
# =====================================================

def obtener_horarios_por_establecimiento(id_establecimiento):
    """Obtiene todos los horarios de un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_HORARIO AS id_horario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                DIA AS dia,
                HORA_INICIO AS hora_inicio,
                HORA_FIN AS hora_fin,
                HORA_INICIO_DESCANSO AS hora_inicio_descanso,
                HORA_FIN_DESCANSO AS hora_fin_descanso,
                ESTADO AS estado
            FROM HORARIO
            WHERE Id_ESTABLECIMIENTO = %s
            ORDER BY FIELD(
                DIA,
                'lunes',
                'martes',
                'miercoles',
                'jueves',
                'viernes',
                'sabado',
                'domingo'
            )
        """

        cursor.execute(consulta, (id_establecimiento,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER HORARIO POR ID
# =====================================================

def obtener_horario_por_id(id_horario, id_establecimiento):
    """Obtiene un horario perteneciente a un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_HORARIO AS id_horario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                DIA AS dia,
                HORA_INICIO AS hora_inicio,
                HORA_FIN AS hora_fin,
                HORA_INICIO_DESCANSO AS hora_inicio_descanso,
                HORA_FIN_DESCANSO AS hora_fin_descanso,
                ESTADO AS estado
            FROM HORARIO
            WHERE Id_HORARIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (id_horario, id_establecimiento)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER HORARIO POR DÍA
# =====================================================

def obtener_horario_por_dia(id_establecimiento, dia):
    """Obtiene el horario completo de un establecimiento para un día."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_HORARIO AS id_horario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                DIA AS dia,
                HORA_INICIO AS hora_inicio,
                HORA_FIN AS hora_fin,
                HORA_INICIO_DESCANSO AS hora_inicio_descanso,
                HORA_FIN_DESCANSO AS hora_fin_descanso,
                ESTADO AS estado
            FROM HORARIO
            WHERE Id_ESTABLECIMIENTO = %s
              AND DIA = %s
            LIMIT 1
        """

        cursor.execute(
            consulta,
            (id_establecimiento, dia)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()



# =====================================================
# CREAR HORARIO
# =====================================================

def crear_horario(
    id_establecimiento,
    dia,
    hora_inicio,
    hora_fin,
    hora_inicio_descanso,
    hora_fin_descanso
):
    """Registra el horario de un día."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO HORARIO (
                Id_ESTABLECIMIENTO,
                DIA,
                HORA_INICIO,
                HORA_FIN,
                HORA_INICIO_DESCANSO,
                HORA_FIN_DESCANSO,
                ESTADO
            )
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """

        cursor.execute(
            consulta,
            (
                id_establecimiento,
                dia,
                hora_inicio,
                hora_fin,
                hora_inicio_descanso,
                hora_fin_descanso
            )
        )

        id_horario = cursor.lastrowid

        conexion.commit()

        return id_horario

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR HORARIO
# =====================================================

def actualizar_horario(
    id_horario,
    id_establecimiento,
    dia,
    hora_inicio,
    hora_fin,
    hora_inicio_descanso,
    hora_fin_descanso
):
    """Actualiza el horario de un día."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE HORARIO
            SET
                DIA = %s,
                HORA_INICIO = %s,
                HORA_FIN = %s,
                HORA_INICIO_DESCANSO = %s,
                HORA_FIN_DESCANSO = %s
            WHERE Id_HORARIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                dia,
                hora_inicio,
                hora_fin,
                hora_inicio_descanso,
                hora_fin_descanso,
                id_horario,
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
# CAMBIAR ESTADO DEL HORARIO
# =====================================================

def actualizar_estado_horario(
    id_horario,
    id_establecimiento,
    estado
):
    """Activa o desactiva un horario."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE HORARIO
            SET ESTADO = %s
            WHERE Id_HORARIO = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                estado,
                id_horario,
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
# LISTAR HORARIOS ACTIVOS PARA CLIENTES
# =====================================================

def obtener_horarios_activos_por_establecimiento(id_establecimiento):
    """Obtiene únicamente los horarios activos de un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_HORARIO AS id_horario,
                Id_ESTABLECIMIENTO AS id_establecimiento,
                DIA AS dia,
                HORA_INICIO AS hora_inicio,
                HORA_FIN AS hora_fin,
                HORA_INICIO_DESCANSO AS hora_inicio_descanso,
                HORA_FIN_DESCANSO AS hora_fin_descanso
            FROM HORARIO
            WHERE Id_ESTABLECIMIENTO = %s
              AND ESTADO = 1
            ORDER BY FIELD(
                DIA,
                'lunes',
                'martes',
                'miercoles',
                'jueves',
                'viernes',
                'sabado',
                'domingo'
            )
        """

        cursor.execute(consulta, (id_establecimiento,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()