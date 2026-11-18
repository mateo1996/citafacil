
from flask import Blueprint

from apps.authentication import views


# =====================================================
# BLUEPRINT DE AUTENTICACIÓN
# =====================================================

authentication_bp = Blueprint(
    "authentication",
    __name__,
    url_prefix="/api/auth"
)


# =====================================================
# RUTAS
# =====================================================

authentication_bp.add_url_rule(
    "/login",
    view_func=views.iniciar_sesion,
    methods=["POST"]
)

authentication_bp.add_url_rule(
    "/verify-email",
    view_func=views.verificar_correo,
    methods=["POST"]
)

authentication_bp.add_url_rule(
    "/forgot-password",
    view_func=views.solicitar_recuperacion,
    methods=["POST"]
)

authentication_bp.add_url_rule(
    "/reset-password",
    view_func=views.restablecer_contrasena,
    methods=["POST"]
)

authentication_bp.add_url_rule(
    "/validate",
    view_func=views.validar_sesion,
    methods=["GET"]
)

authentication_bp.add_url_rule(
    "/logout",
    view_func=views.cerrar_sesion,
    methods=["POST"]
)
