
/* =================================
   1. ELEMENTOS DEL FORMULARIO
================================= */

const loginForm = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const togglePassword = document.querySelector(".toggle-password");
const formMessage = document.querySelector(".form-message");


/* =================================
   2. MOSTRAR Y OCULTAR CONTRASEÑA
================================= */

if (togglePassword && passwordInput) {

    togglePassword.addEventListener("click", function () {

        const isPassword = passwordInput.type === "password";

        passwordInput.type = isPassword ? "text" : "password";

        togglePassword.textContent = isPassword ? "🙈" : "👁";

        togglePassword.setAttribute(
            "aria-label",
            isPassword ? "Ocultar contraseña" : "Mostrar contraseña"
        );

    });

}


/* =================================
   3. VALIDAR CORREO
================================= */

function validarCorreo(correo) {

    const expresion = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return expresion.test(correo);

}


/* =================================
   4. MOSTRAR MENSAJES
================================= */

function mostrarMensaje(mensaje, tipo = "error") {

    if (!formMessage) return;

    formMessage.textContent = mensaje;

    formMessage.style.color =
        tipo === "error" ? "#B54747" : "#20A486";

}


/* =================================
   5. INICIAR SESIÓN
================================= */

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const correo = emailInput.value.trim().toLowerCase();
        const contrasena = passwordInput.value;

        if (!correo || !contrasena.trim()) {
            mostrarMensaje("Por favor, completa todos los campos.");
            return;
        }

        if (!validarCorreo(correo)) {
            mostrarMensaje("Ingresa un correo electrónico válido.");
            emailInput.focus();
            return;
        }

        if (contrasena.length < 8) {
            mostrarMensaje(
                "La contraseña debe tener al menos 8 caracteres."
            );
            passwordInput.focus();
            return;
        }

        if (!window.API) {
            mostrarMensaje("No se pudo conectar con el servidor.");
            return;
        }

        const botonEnviar = loginForm.querySelector(
            'button[type="submit"]'
        );

        if (botonEnviar) {
            botonEnviar.disabled = true;
        }

        mostrarMensaje("Iniciando sesión...", "success");

        try {

            const respuesta = await window.API.post(
                "/auth/login",
                {
                    correo: correo,
                    contrasena: contrasena
                }
            );

            if (!respuesta.ok) {
                mostrarMensaje(
                    respuesta.mensaje || "No se pudo iniciar sesión."
                );
                return;
            }

            const tipoCuenta = respuesta.data?.tipo_cuenta;

            mostrarMensaje(
                "Inicio de sesión exitoso. Redirigiendo...",
                "success"
            );

            if (tipoCuenta === "establecimiento") {

                window.location.href = "/establishment";

            } else if (tipoCuenta === "cliente") {

                window.location.href = "/user";

            } else {

                mostrarMensaje(
                    "No se pudo identificar el tipo de cuenta."
                );

            }

        } catch (error) {

            console.error("Error al iniciar sesión:", error);

            mostrarMensaje(
                error.message || "Ocurrió un error al iniciar sesión."
            );

        } finally {

            if (botonEnviar) {
                botonEnviar.disabled = false;
            }

        }

    });

}