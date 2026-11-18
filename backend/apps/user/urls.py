
from flask import Blueprint

from apps.user import views


# =====================================================
# BLUEPRINT DE CLIENTES
# =====================================================

user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/api/users"
)


# =====================================================
# RUTAS DE CLIENTES
# =====================================================

# Registrar cliente
user_bp.add_url_rule(
    "/register",
    view_func=views.registrar_usuario,
    methods=["POST"]
)

# Obtener perfil propio
user_bp.add_url_rule(
    "/<int:id_usuario>",
    view_func=views.obtener_usuario,
    methods=["GET"]
)

# Actualizar perfil propio
user_bp.add_url_rule(
    "/<int:id_usuario>",
    view_func=views.actualizar_usuario,
    methods=["PUT"]
)

# Listar citas del usuario autenticado
user_bp.add_url_rule(
    "/appointments",
    view_func=views.listar_citas_usuario,
    methods=["GET"]
)

# Crear cita del usuario autenticado
user_bp.add_url_rule(
    "/appointments",
    view_func=views.crear_cita_usuario,
    methods=["POST"]
)