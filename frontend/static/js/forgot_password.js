document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("forgotPasswordForm");
    const emailInput = document.getElementById("email");
    const message = document.getElementById("forgotMessage");
    const button = document.getElementById("forgotButton");

    function mostrarMensaje(texto, tipo = "error") {
        message.textContent = texto;
        message.className = `forgot-message ${tipo}`;
    }

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const correo = emailInput.value.trim().toLowerCase();

        message.textContent = "";
        message.className = "forgot-message";

        if (!correo) {
            mostrarMensaje("Ingresa tu correo electrónico.");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(correo)) {
            mostrarMensaje("Ingresa un correo electrónico válido.");
            return;
        }

        if (!window.API) {
            mostrarMensaje("No se pudo conectar con el servidor.");
            return;
        }

        button.disabled = true;
        button.textContent = "Enviando...";

        try {

            const respuesta = await window.API.post(
                "/auth/forgot-password",
                { correo: correo }
            );

            if (!respuesta.ok) {
                mostrarMensaje(
                    respuesta.mensaje || "No se pudo procesar la solicitud."
                );
                return;
            }

            mostrarMensaje(
                respuesta.mensaje ||
                "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.",
                "success"
            );

            form.reset();

        } catch (error) {

            mostrarMensaje(
                error.message || "Ocurrió un error al solicitar la recuperación."
            );

        } finally {

            button.disabled = false;
            button.textContent = "Enviar enlace";

        }

    });

});