
from apps.clients.views import clients_bp


def registrar_rutas(app):

    app.register_blueprint(
        clients_bp,
        url_prefix="/api/clients"
    )
