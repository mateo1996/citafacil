
document.addEventListener("DOMContentLoaded", () => {

    const appointmentsContainer = document.getElementById(
        "appointmentsContainer"
    );

    const totalAppointments = document.getElementById(
        "totalAppointments"
    );

    const pendingAppointments = document.getElementById(
        "pendingAppointments"
    );

    const confirmedAppointments = document.getElementById(
        "confirmedAppointments"
    );

    const userName = document.getElementById("userName");
    const userAvatar = document.getElementById("userAvatar");
    const welcomeTitle = document.getElementById("welcomeTitle");
    const logoutButton = document.getElementById("logoutButton");


    // =================================
    // UTILIDADES
    // =================================

    function escaparHTML(valor) {
        return String(valor ?? "").replace(/[&<>"']/g, caracter => {
            const entidades = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return entidades[caracter];
        });
    }


    function formatearFecha(fecha) {
        if (!fecha) {
            return "Fecha no disponible";
        }

        const partes = String(fecha).substring(0, 10).split("-");

        if (partes.length !== 3) {
            return escaparHTML(fecha);
        }

        const [anio, mes, dia] = partes;

        return `${dia}/${mes}/${anio}`;
    }


    function formatearHora(hora) {
        if (!hora) {
            return "Hora no disponible";
        }

        return String(hora).substring(0, 5);
    }


    function formatearPrecio(precio) {
        const valor = Number(precio);

        if (!Number.isFinite(valor)) {
            return "No disponible";
        }

        return valor.toLocaleString("es-CO", {
            style: "currency",
            currency: "COP",
            maximumFractionDigits: 0
        });
    }


    function normalizarEstado(estado) {
        return String(estado ?? "")
            .trim()
            .toLowerCase();
    }


    function obtenerTextoEstado(estado) {
        const estados = {
            pendiente: "Pendiente",
            confirmada: "Confirmada",
            completada: "Completada",
            cancelada: "Cancelada"
        };

        return estados[normalizarEstado(estado)] || "Sin estado";
    }


    // =================================
    // PERFIL DEL CLIENTE
    // =================================

    async function cargarPerfil() {
        try {
            const respuesta = await API.get("/auth/validate");

            if (!respuesta.ok) {
                window.location.href = "/";
                return false;
            }

            const usuario = respuesta.data?.usuario;

            if (!usuario) {
                window.location.href = "/";
                return false;
            }

            const nombre = usuario.nombre || "Usuario";

            userName.textContent = nombre;
            userAvatar.textContent = nombre.trim().charAt(0).toUpperCase();
            welcomeTitle.textContent = `¡Bienvenido, ${nombre}!`;
            return true;
        } catch (error) {
            console.error("Error al consultar la sesión:", error);
            window.location.href = "/";
            return false;
        }
    }


    // =================================
    // ESTADÍSTICAS
    // =================================

    function actualizarEstadisticas(citas) {
        const pendientes = citas.filter(cita =>
            normalizarEstado(cita.estado) === "pendiente"
        ).length;

        const confirmadas = citas.filter(cita =>
            normalizarEstado(cita.estado) === "confirmada"
        ).length;

        totalAppointments.textContent = citas.length;
        pendingAppointments.textContent = pendientes;
        confirmedAppointments.textContent = confirmadas;
    }


    // =================================
    // TARJETA DE CITA
    // =================================

    function crearTarjetaCita(cita) {
        const estado = normalizarEstado(cita.estado);

        const nombreEstablecimiento = escaparHTML(
            cita.nombre_establecimiento || "Establecimiento"
        );

        const nombreServicio = escaparHTML(
            cita.nombre_servicio || "Servicio"
        );

        const direccion = escaparHTML(
            cita.direccion_establecimiento || "Dirección no disponible"
        );

        const fecha = formatearFecha(cita.fecha);
        const hora = formatearHora(cita.hora_inicio);
        const precio = formatearPrecio(cita.precio);

        const claseEstado = [
            "pendiente",
            "confirmada",
            "completada",
            "cancelada"
        ].includes(estado) ? estado : "";

        return `
            <article class="appointment-card">

                <div class="appointment-information">

                    <h3>${nombreServicio}</h3>

                    <p>
                        <strong>Establecimiento:</strong>
                        ${nombreEstablecimiento}
                    </p>

                    <p>
                        <strong>Dirección:</strong>
                        ${direccion}
                    </p>

                    <div class="appointment-details">
                        <span>📅 ${fecha}</span>
                        <span>🕒 ${hora}</span>
                        <span>💰 ${precio}</span>
                    </div>

                </div>

                <span class="status-badge ${claseEstado}">
                    ${escaparHTML(obtenerTextoEstado(estado))}
                </span>

            </article>
        `;
    }


    // =================================
    // MOSTRAR CITAS
    // =================================

    function mostrarCitas(citas) {
        if (!Array.isArray(citas) || citas.length === 0) {
            appointmentsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>Aún no tienes citas agendadas</h3>
                    <p>
                        Cuando reserves una cita, aparecerá aquí.
                    </p>
                    <a href="/user/calendar" class="primary-button">
                        Agendar mi primera cita
                    </a>
                </div>
            `;

            return;
        }

        appointmentsContainer.innerHTML = citas
            .map(crearTarjetaCita)
            .join("");
    }


    // =================================
    // CONSULTAR CITAS DEL CLIENTE
    // =================================

    async function cargarCitas() {
        appointmentsContainer.innerHTML = `
            <div class="loading-state">
                Cargando tus citas...
            </div>
        `;

        try {
            const respuesta = await API.get("/users/appointments");

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible consultar tus citas."
                );
            }

            const citas = respuesta.data || [];

            actualizarEstadisticas(citas);
            mostrarCitas(citas);

        } catch (error) {
            console.error("Error al cargar las citas:", error);

            appointmentsContainer.innerHTML = `
                <div class="error-state">
                    No fue posible cargar tus citas.
                    Intenta nuevamente.
                </div>
            `;
        }
    }


    // =================================
    // CERRAR SESIÓN
    // =================================

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


    // =================================
    // INICIALIZACIÓN
    // =================================

    async function inicializarPanel() {
    const sesionValida = await cargarPerfil();

    if (sesionValida) {
        await cargarCitas();
    }
}

    inicializarPanel();

});
