
from flask import Flask, request, Response
import requests


# =====================================================
# CONFIGURACIÓN
# =====================================================

FRONTEND_URL = "http://127.0.0.1:5001"
BACKEND_URL = "http://127.0.0.1:5000"

PROXY_PORT = 5002

app = Flask(__name__, static_folder=None)


# =====================================================
# SERVIDOR DESTINO
# =====================================================

def obtener_servidor_destino():

    if request.path.startswith("/api/") or request.path == "/api":
        return BACKEND_URL

    return FRONTEND_URL


# =====================================================
# PROXY
# =====================================================

@app.route(
    "/",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
@app.route(
    "/<path:path>",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
def proxy(path):

    servidor = obtener_servidor_destino()

    url = servidor + request.path

    if request.query_string:
        url += "?" + request.query_string.decode("latin-1")

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in [
            "host",
            "content-length",
            "connection",
            "transfer-encoding"
        ]
    }

    try:

        respuesta = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=60
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection"
        ]

        respuesta_proxy = Response(
            respuesta.content,
            status=respuesta.status_code
        )

        for key, value in respuesta.headers.items():

            if key.lower() not in excluded_headers:
                respuesta_proxy.headers.add(key, value)

        # Conservar las cookies originales
        for cookie in respuesta.raw.headers.getlist("Set-Cookie"):
            respuesta_proxy.headers.add("Set-Cookie", cookie)

        return respuesta_proxy

    except requests.RequestException as error:

        print("Error en el proxy:", error)

        return Response(
            "Error de conexión con el servidor.",
            status=502
        )


# =====================================================
# INICIAR
# =====================================================

if __name__ == "__main__":

    print("CITAFACIL - PROXY")
    print("Frontend:", FRONTEND_URL)
    print("Backend:", BACKEND_URL)
    print("Proxy: http://127.0.0.1:5002")

    app.run(
        host="127.0.0.1",
        port=PROXY_PORT,
        debug=False,
        threaded=True
    )
