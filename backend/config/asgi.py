from asgiref.wsgi import WsgiToAsgi
from backend.app import app

asgi_app = WsgiToAsgi(app)