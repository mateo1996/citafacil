
from flask import Flask, request
from config import settings

from apps.user.urls import user_bp
from apps.authentication.urls import authentication_bp
from apps.establishment.urls import establishment_bp
from apps.services.urls import service_bp
from apps.schedules.urls import schedule_bp
from apps.appointments.urls import appointment_bp
from apps.clients.urls import clients_bp
from apps.whatsapp.urls import registrar_rutas as registrar_rutas_whatsapp
app = Flask(__name__)

FRONTEND_ORIGIN = "http://127.0.0.1:5001"


# =====================================================
# CONFIGURACIÓN CORS
# =====================================================

@app.after_request
def configurar_cors(response):

    origin = request.headers.get("Origin")

    if origin == FRONTEND_ORIGIN:

        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Vary"] = "Origin"

    return response


# =====================================================
# REGISTRO DE BLUEPRINTS
# =====================================================

app.register_blueprint(user_bp)
app.register_blueprint(authentication_bp)
app.register_blueprint(establishment_bp)
app.register_blueprint(service_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(clients_bp, url_prefix="/api/clients")
registrar_rutas_whatsapp(app)

# =====================================================
# EJECUCIÓN
# =====================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=settings.DEBUG
    )
