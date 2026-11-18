from flask import Fask, render_template

app = Fask(__name__)

app.config.from_object("backend.config.settings")

@app.route("/")
def inicio():
    return "Bienvenido a CitaFacil"

@app.route("/register")
def registro():
    return "Página de registro"


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])