
document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("resetPasswordForm");
    const newPassword = document.getElementById("newPassword");
    const confirmPassword = document.getElementById("confirmPassword");
    const message = document.getElementById("resetMessage");
    const resetButton = document.getElementById("resetButton");

    // =============================================
    // OBTENER TOKEN DE LA URL
    // =============================================

    const parametros = new URLSearchParams(window.location.search);
    const token = parametros.get("token");

    // =============================================
    // MOSTRAR MENSAJES
    // =============================================

    function mostrarMensaje(texto, tipo = "error") {
        message.textContent = texto;
        message.className = `reset-message ${tipo}`;
    }

    // =============================================
    // COMPROBAR TOKEN
    // =============================================

    if (!token || !token.trim()) {
        mostrarMensaje(
            "El enlace de recuperación no es válido. Solicita uno nuevo.",
            "error"
        );

        resetButton.disabled = true;
        return;
    }

    // =============================================
    // MOSTRAR / OCULTAR CONTRASEÑA
    // =============================================

    document.querySelectorAll(".toggle-password").forEach(button => {

        button.addEventListener("click", () => {

            const input = document.getElementById(
                button.dataset.target
            );

            if (!input) return;

            const mostrar = input.type === "password";

            input.type = mostrar ? "text" : "password";

            button.setAttribute(
                "aria-label",
                mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
            );

            button.textContent = mostrar ? "◉" : "👁";

        });

    });

    // =============================================
    // ENVIAR NUEVA CONTRASEÑA
    // =============================================

    form.addEventListener("submit", async event => {

        event.preventDefault();

        const contrasena = newPassword.value;
        const confirmar = confirmPassword.value;

        mostrarMensaje("");

        // Validar longitud.
        if (contrasena.length < 8 || contrasena.length > 128) {
            mostrarMensaje(
                "La contraseña debe tener entre 8 y 128 caracteres."
            );
            return;
        }

        // Validar coincidencia.
        if (contrasena !== confirmar) {
            mostrarMensaje(
                "Las contraseñas no coinciden."
            );
            return;
        }

        // Comprobar API.
        if (!window.API) {
            mostrarMensaje(
                "No fue posible conectar con el servidor."
            );
            return;
        }

        resetButton.disabled = true;
        resetButton.textContent = "Actualizando...";

        try {

            const respuesta = await window.API.post("/auth/reset-password", {
                token: token,
                nueva_contrasena: contrasena,
                confirmar_contrasena: confirmar
            });

            if (!respuesta.ok) {
                mostrarMensaje(
                    respuesta.mensaje || "No fue posible actualizar la contraseña."
                );
                return;
            }

            mostrarMensaje(
                respuesta.mensaje || "Tu contraseña se actualizó correctamente.",
                "success"
            );

            form.reset();

            // El token ya fue utilizado.
            resetButton.disabled = true;

        } catch (error) {

            mostrarMensaje(
                error.message || "Ocurrió un error al actualizar la contraseña."
            );

        } finally {

            resetButton.textContent = "Actualizar contraseña";

            if (message.classList.contains("success")) {
                resetButton.disabled = true;
            } else {
                resetButton.disabled = false;
            }

        }

    });

});
