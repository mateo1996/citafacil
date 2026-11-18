
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS DEL DOM
    // =====================================

    const userName = document.getElementById("userName");
    const userAvatar = document.getElementById("userAvatar");

    const profileForm = document.getElementById("profileForm");
    const profileName = document.getElementById("profileName");
    const profileEmail = document.getElementById("profileEmail");
    const profilePhone = document.getElementById("profilePhone");
    const profileEmailStatus = document.getElementById("profileEmailStatus");

    const profileMessage = document.getElementById("profileMessage");
    const saveProfileButton = document.getElementById("saveProfileButton");
    const logoutButton = document.getElementById("logoutButton");

    let idUsuario = null;


    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(mensaje, tipo) {

        profileMessage.textContent = mensaje;
        profileMessage.className = `profile-status ${tipo}`;

    }


    function limpiarMensaje() {

        profileMessage.textContent = "";
        profileMessage.className = "profile-status";

    }


    // =====================================
    // VALIDAR SESIÓN
    // =====================================

    async function validarSesion() {

        try {

            const respuesta = await API.get("/auth/validate");

            if (!respuesta.ok || respuesta.data?.tipo_cuenta !== "cliente") {
                window.location.href = "/";
                return false;
            }

            const usuario = respuesta.data?.usuario;

            if (!usuario || !usuario.id_usuario) {
                window.location.href = "/";
                return false;
            }

            idUsuario = usuario.id_usuario;

            const nombre = usuario.nombre || "Usuario";

            userName.textContent = nombre;
            userAvatar.textContent = nombre.trim().charAt(0).toUpperCase();

            return true;

        } catch (error) {

            console.error("Error al validar sesión:", error);
            window.location.href = "/";
            return false;

        }

    }


    // =====================================
    // CARGAR PERFIL
    // =====================================

    async function cargarPerfil() {

        try {

            const respuesta = await API.get(`/users/${idUsuario}`);

            if (!respuesta.ok || !respuesta.data) {
                throw new Error(
                    respuesta.mensaje || "No fue posible consultar tu perfil."
                );
            }

            const usuario = respuesta.data;

            profileName.value = usuario.nombre || "";
            profileEmail.value = usuario.correo || "";
            profilePhone.value = usuario.telefono || "";

            profileEmailStatus.value = usuario.correo_verificado
                ? "Correo verificado"
                : "Correo pendiente de verificación";

        } catch (error) {

            console.error("Error al cargar perfil:", error);

            mostrarMensaje(
                error.message || "No fue posible cargar tu perfil.",
                "error"
            );

            profileForm.querySelectorAll("input, button").forEach(elemento => {
                if (elemento.id !== "logoutButton") {
                    elemento.disabled = true;
                }
            });

        }

    }


    // =====================================
    // ACTUALIZAR PERFIL
    // =====================================

    profileForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        limpiarMensaje();

        const datos = {
            nombre: profileName.value.trim(),
            correo: profileEmail.value.trim(),
            telefono: profilePhone.value.trim()
        };

        if (!datos.telefono) {

            mostrarMensaje(
                "Debes registrar tu número de teléfono para reservar citas.",
                "error"
            );

            profilePhone.focus();
            return;

        }

        saveProfileButton.disabled = true;
        saveProfileButton.textContent = "Guardando...";

        try {

            const respuesta = await API.put(
                `/users/${idUsuario}`,
                datos
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible actualizar tu perfil."
                );
            }

            mostrarMensaje(
                respuesta.mensaje || "Tu perfil fue actualizado correctamente.",
                "success"
            );

            userName.textContent = datos.nombre;
            userAvatar.textContent = datos.nombre.charAt(0).toUpperCase();

            if (respuesta.data?.correo_verificado === false) {

                profileEmailStatus.value = "Correo pendiente de verificación";

            }

        } catch (error) {

            mostrarMensaje(
                error.message || "Ocurrió un error al actualizar tu perfil.",
                "error"
            );

        } finally {

            saveProfileButton.disabled = false;
            saveProfileButton.textContent = "Guardar cambios";

        }

    });


    // =====================================
    // CERRAR SESIÓN
    // =====================================

    logoutButton.addEventListener("click", async () => {

        logoutButton.disabled = true;

        try {

            await API.post("/auth/logout", {});

        } catch (error) {

            console.error("Error al cerrar sesión:", error);

        } finally {

            window.location.href = "/";

        }

    });


    // =====================================
    // INICIALIZACIÓN
    // =====================================

    async function inicializarPerfil() {

        const sesionValida = await validarSesion();

        if (!sesionValida) {
            return;
        }

        await cargarPerfil();

    }

    inicializarPerfil();

});
