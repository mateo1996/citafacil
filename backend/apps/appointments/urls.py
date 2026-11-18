
from flask import Blueprint

from apps.appointments import views


# =====================================================
# BLUEPRINT DE CITAS
# =====================================================

appointment_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/api/appointments"
)


# =====================================================
# LISTAR CITAS
# =====================================================

appointment_bp.route(
    "/",
    methods=["GET"]
)(views.listar_citas)


# =====================================================
# CONSULTAR PRÓXIMAS CITAS
# =====================================================

appointment_bp.route(
    "/upcoming",
    methods=["GET"]
)(views.listar_proximas_citas)


# =====================================================
# CONSULTAR UNA CITA
# =====================================================

appointment_bp.route(
    "/<int:id_cita>",
    methods=["GET"]
)(views.consultar_cita)


# =====================================================
# REGISTRAR CITA
# =====================================================

appointment_bp.route(
    "/",
    methods=["POST"]
)(views.registrar_cita)


# =====================================================
# ACTUALIZAR CITA
# =====================================================

appointment_bp.route(
    "/<int:id_cita>",
    methods=["PUT"]
)(views.actualizar_cita)


# =====================================================
# CAMBIAR ESTADO
# =====================================================

appointment_bp.route(
    "/<int:id_cita>/status",
    methods=["PATCH"]
)(views.cambiar_estado_cita)
