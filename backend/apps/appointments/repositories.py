
from infrastructure.database.mysql_db import obtener_conexion


# =====================================================
# LISTAR CITAS DE UN ESTABLECIMIENTO
# =====================================================

def obtener_citas_por_establecimiento(
    id_establecimiento,
    fecha_desde=None,
    fecha_hasta=None,
    estado=None
):
    """Obtiene las citas de un establecimiento con filtros opcionales."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                c.Id_CITA AS id_cita,
                c.Id_ESTABLECIMIENTO AS id_establecimiento,
                c.Id_CLIENTE AS id_cliente,
                c.Id_SERVICIO AS id_servicio,
                c.FECHA AS fecha,
                c.HORA_INICIO AS hora_inicio,
                c.HORA_FIN AS hora_fin,
                c.ESTADO AS estado,
                c.FECHA_CREACION AS fecha_creacion,

                cl.NOMBRE AS nombre_cliente,
                cl.TELEFONO AS telefono_cliente,
                cl.CORREO AS correo_cliente,

                s.NOMBRE AS nombre_servicio,
                s.DURACION_MINUTOS AS duracion_minutos,
                s.PRECIO AS precio

            FROM CITA c

            INNER JOIN CLIENTE cl
                ON c.Id_CLIENTE = cl.Id_CLIENTE

            INNER JOIN SERVICIO s
                ON c.Id_SERVICIO = s.Id_SERVICIO

            WHERE c.Id_ESTABLECIMIENTO = %s
        """

        parametros = [id_establecimiento]

        if fecha_desde:
            consulta += " AND c.FECHA >= %s"
            parametros.append(fecha_desde)

        if fecha_hasta:
            consulta += " AND c.FECHA <= %s"
            parametros.append(fecha_hasta)

        if estado:
            consulta += " AND c.ESTADO = %s"
            parametros.append(estado)

        consulta += """
            ORDER BY c.FECHA ASC, c.HORA_INICIO ASC
        """

        cursor.execute(consulta, tuple(parametros))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CONSULTAR PRÓXIMAS CITAS
# =====================================================

def obtener_proximas_citas(id_establecimiento, limite=5):
    """Obtiene las próximas citas pendientes y confirmadas."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                c.Id_CITA AS id_cita,
                c.FECHA AS fecha,
                c.HORA_INICIO AS hora_inicio,
                c.HORA_FIN AS hora_fin,
                c.ESTADO AS estado,

                cl.NOMBRE AS nombre_cliente,
                cl.TELEFONO AS telefono_cliente,

                s.NOMBRE AS nombre_servicio,
                s.DURACION_MINUTOS AS duracion_minutos,
                s.PRECIO AS precio

            FROM CITA c

            INNER JOIN CLIENTE cl
                ON c.Id_CLIENTE = cl.Id_CLIENTE

            INNER JOIN SERVICIO s
                ON c.Id_SERVICIO = s.Id_SERVICIO

            WHERE c.Id_ESTABLECIMIENTO = %s
              AND c.FECHA >= CURDATE()
              AND c.ESTADO IN ('pendiente', 'confirmada')

            ORDER BY
                c.FECHA ASC,
                c.HORA_INICIO ASC

            LIMIT %s
        """

        cursor.execute(
            consulta,
            (id_establecimiento, limite)
        )

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER UNA CITA POR ID
# =====================================================

def obtener_cita_por_id(id_cita, id_establecimiento):
    """Obtiene una cita perteneciente a un establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                c.Id_CITA AS id_cita,
                c.Id_ESTABLECIMIENTO AS id_establecimiento,
                c.Id_CLIENTE AS id_cliente,
                c.Id_SERVICIO AS id_servicio,
                c.FECHA AS fecha,
                c.HORA_INICIO AS hora_inicio,
                c.HORA_FIN AS hora_fin,
                c.ESTADO AS estado,
                c.FECHA_CREACION AS fecha_creacion,

                cl.NOMBRE AS nombre_cliente,
                cl.TELEFONO AS telefono_cliente,
                cl.CORREO AS correo_cliente,

                s.NOMBRE AS nombre_servicio,
                s.DURACION_MINUTOS AS duracion_minutos,
                s.PRECIO AS precio

            FROM CITA c

            INNER JOIN CLIENTE cl
                ON c.Id_CLIENTE = cl.Id_CLIENTE

            INNER JOIN SERVICIO s
                ON c.Id_SERVICIO = s.Id_SERVICIO

            WHERE c.Id_CITA = %s
              AND c.Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (id_cita, id_establecimiento)
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# OBTENER CLIENTE POR ID
# =====================================================

def obtener_cliente_por_id(id_cliente, id_establecimiento):
    """Consulta un cliente perteneciente a un establecimiento."""

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
# LISTAR CLIENTES
# =====================================================

def obtener_todos_los_clientes(id_establecimiento):
    """Obtiene los clientes de un establecimiento."""

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

        cursor.execute(
            consulta,
            (id_establecimiento,)
        )

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()



# =====================================================
# OBTENER SERVICIO ACTIVO
# =====================================================

def obtener_servicio_activo(
    id_servicio,
    id_establecimiento
):
    """Consulta un servicio activo del establecimiento."""

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
                DURACION_MINUTOS AS duracion_minutos,
                PRECIO AS precio,
                ESTADO AS estado
            FROM SERVICIO
            WHERE Id_SERVICIO = %s
              AND Id_ESTABLECIMIENTO = %s
              AND ESTADO = 1
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
# VALIDAR DISPONIBILIDAD DE HORARIO
# =====================================================

def existe_conflicto_horario(
    id_establecimiento,
    fecha,
    hora_inicio,
    hora_fin,
    id_cita=None
):
    """
    Comprueba si existe una cita pendiente o confirmada
    que se cruce con el horario solicitado.
    """

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT Id_CITA AS id_cita
            FROM CITA
            WHERE Id_ESTABLECIMIENTO = %s
              AND FECHA = %s
              AND ESTADO IN ('pendiente', 'confirmada')
              AND HORA_INICIO < %s
              AND HORA_FIN > %s
        """

        parametros = [
            id_establecimiento,
            fecha,
            hora_fin,
            hora_inicio
        ]

        if id_cita is not None:
            consulta += " AND Id_CITA != %s"
            parametros.append(id_cita)

        consulta += " LIMIT 1"

        cursor.execute(consulta, tuple(parametros))

        return cursor.fetchone() is not None

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# CREAR CITA
# =====================================================

def crear_cita(
    id_establecimiento,
    id_cliente,
    id_servicio,
    fecha,
    hora_inicio,
    hora_fin
):
    """Registra una nueva cita."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO CITA (
                Id_ESTABLECIMIENTO,
                Id_CLIENTE,
                Id_SERVICIO,
                FECHA,
                HORA_INICIO,
                HORA_FIN,
                ESTADO
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
        """

        cursor.execute(
            consulta,
            (
                id_establecimiento,
                id_cliente,
                id_servicio,
                fecha,
                hora_inicio,
                hora_fin
            )
        )

        id_cita = cursor.lastrowid

        conexion.commit()

        return id_cita

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR CITA
# =====================================================

def actualizar_cita(
    id_cita,
    id_establecimiento,
    id_cliente,
    id_servicio,
    fecha,
    hora_inicio,
    hora_fin
):
    """Actualiza los datos de una cita."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE CITA
            SET
                Id_CLIENTE = %s,
                Id_SERVICIO = %s,
                FECHA = %s,
                HORA_INICIO = %s,
                HORA_FIN = %s
            WHERE Id_CITA = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                id_cliente,
                id_servicio,
                fecha,
                hora_inicio,
                hora_fin,
                id_cita,
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
# CAMBIAR ESTADO DE UNA CITA
# =====================================================

def actualizar_estado_cita(
    id_cita,
    id_establecimiento,
    estado
):
    """Actualiza el estado de una cita."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE CITA
            SET ESTADO = %s
            WHERE Id_CITA = %s
              AND Id_ESTABLECIMIENTO = %s
        """

        cursor.execute(
            consulta,
            (
                estado,
                id_cita,
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
# OBTENER HORARIO DE UN DÍA
# =====================================================

def obtener_horario_por_dia(id_establecimiento, dia):
    """Obtiene el horario activo de un día del establecimiento."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                Id_HORARIO AS id_horario,
                DIA AS dia,
                HORA_INICIO AS hora_inicio,
                HORA_FIN AS hora_fin,
                HORA_INICIO_DESCANSO AS hora_inicio_descanso,
                HORA_FIN_DESCANSO AS hora_fin_descanso,
                ESTADO AS estado
            FROM HORARIO
            WHERE Id_ESTABLECIMIENTO = %s
              AND DIA = %s
              AND ESTADO = 1
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
# REGISTRAR NOTIFICACIÓN DE CONFIRMACIÓN
# =====================================================

def registrar_notificacion_confirmacion_whatsapp(id_cita):
    """Registra una notificación evitando duplicados."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT IGNORE INTO NOTIFICACION (
                Id_CITA,
                CANAL,
                TIPO,
                ESTADO
            )
            VALUES (%s, 'whatsapp', 'confirmacion', 'pendiente')
        """

        cursor.execute(consulta, (id_cita,))
        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas == 1

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =====================================================
# ACTUALIZAR NOTIFICACIÓN DE WHATSAPP
# =====================================================

def actualizar_notificacion_whatsapp(
    id_cita,
    estado,
    respuesta
):
    """Actualiza el resultado del envío de WhatsApp."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE NOTIFICACION
            SET
                ESTADO = %s,
                INTENTOS = INTENTOS + 1,
                RESPUESTA = %s,
                FECHA_ENVIO = CASE
                    WHEN %s = 'enviada' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE Id_CITA = %s
              AND CANAL = 'whatsapp'
              AND TIPO = 'confirmacion'
        """

        cursor.execute(
            consulta,
            (estado, respuesta, estado, id_cita)
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
        

# =====================================================
# LISTAR CITAS DE UN CLIENTE AUTENTICADO
# =====================================================

def obtener_citas_por_usuario(id_usuario):
    """Obtiene únicamente las citas asociadas al usuario."""

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                c.Id_CITA AS id_cita,
                c.FECHA AS fecha,
                c.HORA_INICIO AS hora_inicio,
                c.HORA_FIN AS hora_fin,
                c.ESTADO AS estado,

                e.NOMBRE_COMERCIAL AS nombre_establecimiento,
                e.DIRECCION AS direccion_establecimiento,

                s.NOMBRE AS nombre_servicio,
                s.DURACION_MINUTOS AS duracion_minutos,
                s.PRECIO AS precio

            FROM CITA c

            INNER JOIN CLIENTE cl
                ON c.Id_CLIENTE = cl.Id_CLIENTE

            INNER JOIN ESTABLECIMIENTO e
                ON c.Id_ESTABLECIMIENTO = e.Id_ESTABLECIMIENTO

            INNER JOIN SERVICIO s
                ON c.Id_SERVICIO = s.Id_SERVICIO

            WHERE cl.Id_USUARIO = %s

            ORDER BY
                c.FECHA DESC,
                c.HORA_INICIO DESC
        """

        cursor.execute(consulta, (id_usuario,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        conexion.close()
        


# =====================================================
# CREAR CITA DESDE UNA CUENTA DE CLIENTE
# =====================================================

def crear_cita_usuario(
    id_usuario,
    id_establecimiento,
    id_servicio,
    fecha,
    dia,
    hora_inicio,
    hora_fin
):
    """
    Crea una cita para un usuario autenticado.

    La creación del cliente y de la cita se realiza
    dentro de una única transacción.
    """

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        # -------------------------------------------------
        # 1. BLOQUEAR EL ESTABLECIMIENTO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT Id_ESTABLECIMIENTO
            FROM ESTABLECIMIENTO
            WHERE Id_ESTABLECIMIENTO = %s
              AND ESTADO = 1
              AND CORREO_VERIFICADO = 1
            FOR UPDATE
            """,
            (id_establecimiento,)
        )

        establecimiento = cursor.fetchone()

        if not establecimiento:
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": "El establecimiento no está disponible."
            }

        # -------------------------------------------------
        # 2. VALIDAR EL USUARIO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                Id_USUARIO AS id_usuario,
                NOMBRE AS nombre,
                CORREO AS correo,
                TELEFONO AS telefono
            FROM USUARIO
            WHERE Id_USUARIO = %s
              AND ESTADO = 1
              AND CORREO_VERIFICADO = 1
            FOR UPDATE
            """,
            (id_usuario,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": "La cuenta no está habilitada para reservar."
            }

        nombre = usuario["nombre"]
        correo = usuario["correo"]
        telefono = usuario["telefono"]

        if not telefono or not telefono.strip():
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": (
                    "Debes registrar tu número de teléfono "
                    "en tu perfil antes de reservar."
                )
            }

        telefono = telefono.strip()

        # -------------------------------------------------
        # 3. VALIDAR EL SERVICIO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT Id_SERVICIO
            FROM SERVICIO
            WHERE Id_SERVICIO = %s
              AND Id_ESTABLECIMIENTO = %s
              AND ESTADO = 1
            LIMIT 1
            """,
            (id_servicio, id_establecimiento)
        )

        servicio = cursor.fetchone()

        if not servicio:
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": "El servicio no está disponible."
            }

        # -------------------------------------------------
        # 4. VALIDAR EL HORARIO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT Id_HORARIO
            FROM HORARIO
            WHERE Id_ESTABLECIMIENTO = %s
              AND DIA = %s
              AND ESTADO = 1
              AND HORA_INICIO <= %s
              AND HORA_FIN >= %s
              AND (
                  HORA_INICIO_DESCANSO IS NULL
                  OR HORA_FIN_DESCANSO IS NULL
                  OR NOT (
                      HORA_INICIO_DESCANSO < %s
                      AND HORA_FIN_DESCANSO > %s
                  )
              )
            LIMIT 1
            """,
            (
                id_establecimiento,
                dia,
                hora_inicio,
                hora_fin,
                hora_fin,
                hora_inicio
            )
        )

        horario = cursor.fetchone()

        if not horario:
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": (
                    "El horario solicitado no está disponible "
                    "dentro de la jornada de atención."
                )
            }

        # -------------------------------------------------
        # 5. COMPROBAR CONFLICTOS DE HORARIO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT Id_CITA
            FROM CITA
            WHERE Id_ESTABLECIMIENTO = %s
              AND FECHA = %s
              AND ESTADO IN ('pendiente', 'confirmada')
              AND HORA_INICIO < %s
              AND HORA_FIN > %s
            LIMIT 1
            """,
            (
                id_establecimiento,
                fecha,
                hora_fin,
                hora_inicio
            )
        )

        conflicto = cursor.fetchone()

        if conflicto:
            conexion.rollback()
            return {
                "ok": False,
                "mensaje": (
                    "El horario seleccionado acaba de ser ocupado. "
                    "Selecciona otro horario."
                )
            }

        # -------------------------------------------------
        # 6. BUSCAR CLIENTE VINCULADO AL USUARIO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT Id_CLIENTE
            FROM CLIENTE
            WHERE Id_USUARIO = %s
              AND Id_ESTABLECIMIENTO = %s
            LIMIT 1
            """,
            (id_usuario, id_establecimiento)
        )

        cliente = cursor.fetchone()

        if cliente:
            id_cliente = cliente["Id_CLIENTE"]

        else:
            # ---------------------------------------------
            # 7. COMPROBAR TELÉFONO DE CLIENTES ANTIGUOS
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT Id_CLIENTE
                FROM CLIENTE
                WHERE Id_ESTABLECIMIENTO = %s
                  AND TELEFONO = %s
                LIMIT 1
                """,
                (id_establecimiento, telefono)
            )

            cliente_existente = cursor.fetchone()

            if cliente_existente:
                conexion.rollback()
                return {
                    "ok": False,
                    "mensaje": (
                        "Tu teléfono ya está registrado en este "
                        "establecimiento. Se requiere una revisión "
                        "manual antes de realizar la reserva."
                    )
                }

            # ---------------------------------------------
            # 8. CREAR CLIENTE VINCULADO AL USUARIO
            # ---------------------------------------------

            cursor.execute(
                """
                INSERT INTO CLIENTE (
                    Id_USUARIO,
                    NOMBRE,
                    TELEFONO,
                    CORREO,
                    Id_ESTABLECIMIENTO
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    id_usuario,
                    nombre,
                    telefono,
                    correo,
                    id_establecimiento
                )
            )

            id_cliente = cursor.lastrowid

        # -------------------------------------------------
        # 9. REGISTRAR LA CITA
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO CITA (
                Id_ESTABLECIMIENTO,
                Id_CLIENTE,
                Id_SERVICIO,
                FECHA,
                HORA_INICIO,
                HORA_FIN,
                ESTADO
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
            """,
            (
                id_establecimiento,
                id_cliente,
                id_servicio,
                fecha,
                hora_inicio,
                hora_fin
            )
        )

        id_cita = cursor.lastrowid

        # -------------------------------------------------
        # 10. CONFIRMAR TRANSACCIÓN
        # -------------------------------------------------

        conexion.commit()

        return {
            "ok": True,
            "id_cita": id_cita,
            "mensaje": "La cita fue reservada correctamente."
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        conexion.close()
