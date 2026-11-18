
document.addEventListener("DOMContentLoaded", () => {

    // =================================
    // ELEMENTOS DEL FORMULARIO
    // =================================

    const establishmentForm = document.getElementById("establishmentForm");

    const nombreInput = document.getElementById("nombre");
    const apellidoInput = document.getElementById("apellido");
    const nombreEstablecimientoInput = document.getElementById("nombreEstablecimiento");
    const emailInput = document.getElementById("email");
    const telefonoInput = document.getElementById("telefono");
    const direccionInput = document.getElementById("direccion");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");

    const termsInput = document.getElementById("terms");
    const messageElement = document.getElementById("establishmentMessage");

    // =================================
    // VERIFICAR ELEMENTOS
    // =================================

    if (
        !establishmentForm ||
        !nombreInput ||
        !apellidoInput ||
        !nombreEstablecimientoInput ||
        !emailInput ||
        !telefonoInput ||
        !direccionInput ||
        !passwordInput ||
        !confirmPasswordInput ||
        !termsInput ||
        !messageElement
    ) {
        console.error(
            "No se encontraron todos los elementos del formulario de establecimientos."
        );
        return;
    }

    // =================================
    // MOSTRAR MENSAJES
    // =================================

    function showMessage(message, type) {
        messageElement.textContent = message;
        messageElement.className = `form-message ${type}`;
    }

    // =================================
    // MOSTRAR Y OCULTAR CONTRASEÑAS
    // =================================

    document.querySelectorAll(".toggle-password").forEach(button => {

        button.addEventListener("click", () => {

            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);

            if (!input) return;

            const mostrar = input.type === "password";

            input.type = mostrar ? "text" : "password";

            button.textContent = mostrar ? "🙈" : "👁";

            button.setAttribute(
                "aria-label",
                mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
            );

        });

    });

    // =================================
    // VALIDAR FORMULARIO
    // =================================

    function validarFormulario() {

        const nombre = nombreInput.value.trim();
        const apellido = apellidoInput.value.trim();

        const nombreEstablecimiento =
            nombreEstablecimientoInput.value.trim();

        const email = emailInput.value.trim().toLowerCase();
        const telefono = telefonoInput.value.trim();
        const direccion = direccionInput.value.trim();

        const contrasena = passwordInput.value;
        const confirmarContrasena = confirmPasswordInput.value;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const telefonoRegex = /^[0-9+\-\s()]+$/;

        if (nombre.length < 2 || nombre.length > 50) {
            throw new Error(
                "El nombre debe tener entre 2 y 50 caracteres."
            );
        }

        if (apellido.length < 2 || apellido.length > 50) {
            throw new Error(
                "El apellido debe tener entre 2 y 50 caracteres."
            );
        }

        if (
            nombreEstablecimiento.length < 2 ||
            nombreEstablecimiento.length > 100
        ) {
            throw new Error(
                "El nombre del establecimiento debe tener entre 2 y 100 caracteres."
            );
        }

        if (!emailRegex.test(email)) {
            throw new Error(
                "Ingresa un correo electrónico válido."
            );
        }

        if (
            telefono &&
            (
                telefono.length > 20 ||
                !telefonoRegex.test(telefono)
            )
        ) {
            throw new Error(
                "El teléfono no tiene un formato válido."
            );
        }

        if (direccion.length < 3 || direccion.length > 100) {
            throw new Error(
                "La dirección debe tener entre 3 y 100 caracteres."
            );
        }

        if (contrasena.length < 8 || contrasena.length > 128) {
            throw new Error(
                "La contraseña debe tener entre 8 y 128 caracteres."
            );
        }

        if (contrasena !== confirmarContrasena) {
            throw new Error(
                "Las contraseñas no coinciden."
            );
        }

        if (!termsInput.checked) {
            throw new Error(
                "Debes aceptar los términos y condiciones."
            );
        }

        return {
            nombre,
            apellido,
            nombre_establecimiento: nombreEstablecimiento,
            email,
            telefono,
            direccion,
            contrasena
        };

    }

    // =================================
    // ENVIAR FORMULARIO
    // =================================

    establishmentForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const boton = establishmentForm.querySelector(
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

            showMessage(
                "Registrando establecimiento...",
                "info"
            );

            const respuesta = await window.API.post(
                "/establishments/register",
                datos
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje ||
                    "No fue posible registrar el establecimiento."
                );
            }

            establishmentForm.reset();

            if (
                respuesta.data &&
                respuesta.data.correo_verificacion_enviado === false
            ) {
                showMessage(
                    respuesta.mensaje,
                    "warning"
                );

                return;
            }

            showMessage(
                respuesta.mensaje ||
                "Registro realizado correctamente. Revisa tu correo para verificar tu cuenta.",
                "success"
            );

        } catch (error) {

            showMessage(
                error.message ||
                "No fue posible completar el registro.",
                "error"
            );

            console.error(
                "Error durante el registro del establecimiento:",
                error
            );

        } finally {

            if (boton) {
                boton.disabled = false;
            }

        }

    });

});
