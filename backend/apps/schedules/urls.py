
from flask import Blueprint

from apps.schedules import views


# =====================================================
# BLUEPRINT DE HORARIOS
# =====================================================

schedule_bp = Blueprint(
    "schedule",
    __name__,
    url_prefix="/api/schedules"
)


# =====================================================
# RUTAS
# =====================================================

# Listar horarios del establecimiento autenticado
schedule_bp.add_url_rule(
    "/",
    view_func=views.listar_horarios,
    methods=["GET"]
)


# Registrar horario
schedule_bp.add_url_rule(
    "/",
    view_func=views.registrar_horario,
    methods=["POST"]
)


# Obtener horario por ID
schedule_bp.add_url_rule(
    "/<int:id_horario>",
    view_func=views.obtener_horario,
    methods=["GET"]
)


# Actualizar horario
schedule_bp.add_url_rule(
    "/<int:id_horario>",
    view_func=views.actualizar_horario,
    methods=["PUT"]
)


# Activar o desactivar horario
schedule_bp.add_url_rule(
    "/<int:id_horario>/status",
    view_func=views.cambiar_estado_horario,
    methods=["PATCH"]
)


# Horarios disponibles para clientes
schedule_bp.add_url_rule(
    "/available/<int:id_establecimiento>",
    view_func=views.listar_horarios_disponibles,
    methods=["GET"]
)