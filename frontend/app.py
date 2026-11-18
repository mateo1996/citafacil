
from flask import Flask, render_template

app = Flask(__name__)


# =====================================================
# PÁGINAS PRINCIPALES
# =====================================================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/register")
def registro():
    return render_template("register.html")


@app.route("/register-establishment")
def register_establishment():
    return render_template("register_establishment.html")


@app.route("/verify-email")
def verificar_correo():
    return render_template("verify_email.html")


@app.route("/reset-password")
def restablecer_contrasena():
    return render_template("reset_password.html")


@app.route("/forgot-password")
def recuperar_contrasena():
    return render_template("forgot_password.html")


# =====================================================
# ESTABLECIMIENTO
# =====================================================

@app.route("/establishment")
def inicio_establecimiento():
    return render_template("establishment/index.html")


# =====================================================
# SERVICIOS
# =====================================================

@app.route("/establishment/services")
def servicios_establecimiento():
    return render_template("establishment/services.html")


# =====================================================
# HORARIOS
# =====================================================

@app.route("/establishment/schedules")
def servicios_horario():
    return render_template("establishment/schedules.html")


# =====================================================
# CITAS
# =====================================================

@app.route("/establishment/appointments")
def servicios_cita():
    return render_template("establishment/appointments.html")


# =====================================================
# CLIENTES
# =====================================================

@app.route("/establishment/clients")
def servicios_cliente():
    return render_template("establishment/clients.html")



# =====================================================
# USUARIO
# =====================================================

@app.route("/user")
def inicio_usuario():
    return render_template("user/home.html")


# =====================================================
# USUARIO - CALENDARIO
# =====================================================

@app.route("/user/calendar")
def calendario_usuario():
    return render_template("user/calendar.html")


# =====================================================
# USUARIO - PERFIL
# =====================================================

@app.route("/user/profile")
def perfil_usuario():
    return render_template("user/profile.html")

# =====================================================
# EJECUCIÓN DEL FRONTEND
# =====================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
