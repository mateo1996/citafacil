
from flask import Blueprint

from apps.services import views


# =====================================================
# BLUEPRINT DE SERVICIOS
# =====================================================

service_bp = Blueprint(
    "service",
    __name__,
    url_prefix="/api/services"
)


# =====================================================
# RUTAS
# =====================================================

# Listar servicios del establecimiento autenticado
service_bp.add_url_rule(
    "/",
    view_func=views.listar_servicios,
    methods=["GET"]
)


# Registrar servicio
service_bp.add_url_rule(
    "/",
    view_func=views.registrar_servicio,
    methods=["POST"]
)


# Obtener servicio por ID
service_bp.add_url_rule(
    "/<int:id_servicio>",
    view_func=views.obtener_servicio,
    methods=["GET"]
)


# Actualizar servicio
service_bp.add_url_rule(
    "/<int:id_servicio>",
    view_func=views.actualizar_servicio,
    methods=["PUT"]
)


# Activar o desactivar servicio
service_bp.add_url_rule(
    "/<int:id_servicio>/status",
    view_func=views.cambiar_estado_servicio,
    methods=["PATCH"]
)


# Listar servicios activos para clientes
service_bp.add_url_rule(
    "/available/<int:id_establecimiento>",
    view_func=views.listar_servicios_disponibles,
    methods=["GET"]
)

