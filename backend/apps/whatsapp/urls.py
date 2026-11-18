
from apps.whatsapp.views import whatsapp_bp


def registrar_rutas(app):
    app.register_blueprint(whatsapp_bp)
