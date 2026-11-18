
document.addEventListener("DOMContentLoaded", async () => {

    const messageElement = document.getElementById("verifyMessage");
    const resendButton = document.getElementById("resendVerification");

    function showMessage(message, type) {

        if (!messageElement) return;

        messageElement.textContent = message;
        messageElement.className = `verify-message ${type}`;
    }

    // =====================================================
    // OBTENER TOKEN DE LA URL
    // =====================================================

    const parametros = new URLSearchParams(window.location.search);
    const token = parametros.get("token");

    if (!token) {
        showMessage(
            "El enlace de verificación no contiene un token válido.",
            "error"
        );
        return;
    }

    // =====================================================
    // VERIFICAR CORREO
    // =====================================================

    if (!window.API) {
        showMessage(
            "No se pudo establecer conexión con el servidor.",
            "error"
        );
        return;
    }

    try {

        showMessage("Verificando correo electrónico...", "info");

        const respuesta = await window.API.post(
            "/auth/verify-email",
            { token: token }
        );

        if (!respuesta.ok) {
            throw new Error(
                respuesta.mensaje || "No se pudo verificar el correo."
            );
        }

        showMessage(
            respuesta.mensaje || "¡Correo verificado correctamente!",
            "success"
        );

        // Retirar el token de la barra de direcciones.
        window.history.replaceState(
            {},
            document.title,
            window.location.pathname
        );

    } catch (error) {

        console.error("Error al verificar correo:", error);

        showMessage(
            error.message || "Ocurrió un error al verificar el correo.",
            "error"
        );

    }

});
