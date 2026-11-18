
from flask import Blueprint

from apps.establishment import views


# =====================================================
# BLUEPRINT DE ESTABLECIMIENTOS
# =====================================================

establishment_bp = Blueprint(
    "establishment",
    __name__,
    url_prefix="/api/establishments"
)


# =====================================================
# RUTAS
# =====================================================

# Registrar establecimiento
establishment_bp.add_url_rule(
    "/register",
    view_func=views.registrar_establecimiento,
    methods=["POST"]
)

# Obtener establecimiento autenticado por ID
establishment_bp.add_url_rule(
    "/<int:id_establecimiento>",
    view_func=views.obtener_establecimiento,
    methods=["GET"]
)



# Listar establecimientos disponibles para clientes
establishment_bp.add_url_rule(
    "/available",
    view_func=views.listar_establecimientos_disponibles,
    methods=["GET"]
)
