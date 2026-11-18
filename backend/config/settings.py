from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# RUTA DEL PROYECTO
BASE_DIR = Path(__file__).resolve().parent.parent

# VARIABLES DE ENTORNO
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# CONFIGURACION GENERAL
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "True").lower() in (
    "true", "1", "yes"
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

LENGUAGE = "es"
TIMEZONE = "America/Bogota"

# CONFIGURACION BASE DE DATOS - MYSQL
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# JWT LLAVES
PASSWORD_JWT = os.getenv("PASSWORD_JWT")
ALGORITHM_JWT = os.getenv("ALGORITHM_JWT", "HS256")

# Expiración general en días
JWT_EXP_DAYS = int(os.getenv("JWT_EXP_DAYS", "7"))

# Verificación de correo en minutos
JWT_EMAIL_VERIFICATION_MINUTES = int(
    os.getenv("JWT_EMAIL_VERIFICATION_MINUTES", "30")
)

# Recuperación de contraseña en minutos
JWT_PASSWORD_RESET_MINUTES = int(
    os.getenv("JWT_PASSWORD_RESET_MINUTES", "15")
)


# CONFIGURACIÓN DEL CORREO ELECTRÓNICO

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))

MAIL_USE_TLS = os.getenv(
    "MAIL_USE_TLS", "True"
).lower() in ("true", "1", "yes")

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

FRONTEND_URL = os.getenv(
    "FRONTEND_URL"
)


# CONFIGURACIÓN DE CODIFICACIÓN
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    except (AttributeError, ValueError):
        pass

# =====================================================
# CONFIGURACIÓN DE CONTRASEÑAS
# =====================================================

PASSWORD_MIN_LENGTH = 8

# =====================================================
# CONFIGURACIÓN DE COOKIES DE SESIÓN
# =====================================================

SESSION_COOKIE_SECURE = (
    ENVIRONMENT == "production"
)

SESSION_COOKIE_SAMESITE = "Lax"


# =====================================================
# CONFIGURACIÓN DE WHATSAPP CLOUD API
# =====================================================

WHATSAPP_PHONE_NUMBER_ID = os.getenv(
    "WHATSAPP_PHONE_NUMBER_ID",
    ""
)

WHATSAPP_API_VERSION = os.getenv(
    "WHATSAPP_API_VERSION",
    "v27.0"
)

WHATSAPP_ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN",
    ""
)

WHATSAPP_VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    ""
)