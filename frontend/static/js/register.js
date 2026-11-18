
document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // ELEMENTOS DEL FORMULARIO
    // =====================================================

    const registerForm = document.getElementById("registerForm");

    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");
    const termsInput = document.getElementById("terms");
    const messageElement = document.getElementById("registerMessage");

    if (
        !registerForm ||
        !nameInput ||
        !emailInput ||
        !passwordInput ||
        !confirmPasswordInput ||
        !termsInput ||
        !messageElement
    ) {
        console.error("No se encontraron todos los elementos del formulario.");
        return;
    }

    // =====================================================
    // MOSTRAR MENSAJES
    // =====================================================

    function showMessage(message, type) {
        messageElement.textContent = message;
        messageElement.className = type;
    }

    // =====================================================
    // MOSTRAR / OCULTAR CONTRASEÑA
    // =====================================================

    document.querySelectorAll(".toggle-password").forEach(button => {

        button.addEventListener("click", () => {

            const input = button.parentElement.querySelector("input");

            if (!input) return;

            input.type = input.type === "password"
                ? "text"
                : "password";

        });

    });

    // =====================================================
    // VALIDAR FORMULARIO
    // =====================================================

    function validarFormulario() {

        const nombre = nameInput.value.trim();
        const correo = emailInput.value.trim();
        const contrasena = passwordInput.value;
        const confirmarContrasena = confirmPasswordInput.value;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (nombre.length < 3) {
            throw new Error("El nombre debe tener al menos 3 caracteres.");
        }

        if (!emailRegex.test(correo)) {
            throw new Error("Ingresa un correo electrónico válido.");
        }

        if (contrasena.length < 8) {
            throw new Error("La contraseña debe tener al menos 8 caracteres.");
        }

        if (contrasena !== confirmarContrasena) {
            throw new Error("Las contraseñas no coinciden.");
        }

        if (!termsInput.checked) {
            throw new Error("Debes aceptar los términos y condiciones.");
        }

        return {
            nombre: nombre,
            correo: correo,
            contrasena: contrasena,
            confirmar_contrasena: confirmarContrasena
        };
    }

    // =====================================================
    // REGISTRAR USUARIO
    // =====================================================

    registerForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const boton = registerForm.querySelector(
            'button[type="submit"]'
        );

        try {

            if (!window.API) {
                throw new Error(
                    "No se ha podido cargar el servicio de conexión."
                );
            }

            const datos = validarFormulario();

            if (boton) {
                boton.disabled = true;
            }

            showMessage("Registrando usuario...", "info");

            const respuesta = await window.API.post(
                "/users/register",
                datos
            );

            showMessage(
                respuesta.mensaje ||
                "Registro realizado correctamente. Revisa tu correo.",
                "success"
            );

            registerForm.reset();

        } catch (error) {

            showMessage(
                error.message ||
                "No fue posible completar el registro.",
                "error"
            );

            console.error("Error durante el registro:", error);

        } finally {

            if (boton) {
                boton.disabled = false;
            }

        }

    });

});
