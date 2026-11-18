
document.addEventListener("DOMContentLoaded", async () => {

    // =====================================================
    // ELEMENTOS DEL DOM
    // =====================================================

    const establishmentName = document.getElementById("establishmentName");
    const adminName = document.getElementById("adminName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const totalAppointments = document.getElementById("totalAppointments");
    const pendingAppointments = document.getElementById("pendingAppointments");
    const confirmedAppointments = document.getElementById("confirmedAppointments");

    const appointmentsTableBody = document.getElementById("appointmentsTableBody");

    const emptyAppointments = document.getElementById("emptyAppointments");
    const loadingAppointments = document.getElementById("loadingAppointments");
    const appointmentsError = document.getElementById("appointmentsError");
    const appointmentsErrorMessage = document.getElementById("appointmentsErrorMessage");
    const retryAppointmentsButton = document.getElementById("retryAppointmentsButton");

    const filterDate = document.getElementById("filterDate");
    const filterStatus = document.getElementById("filterStatus");
    const clearFiltersButton = document.getElementById("clearFiltersButton");

    const appointmentModal = document.getElementById("appointmentModal");
    const appointmentForm = document.getElementById("appointmentForm");
    const appointmentId = document.getElementById("appointmentId");

    const appointmentClient = document.getElementById("appointmentClient");
    const appointmentService = document.getElementById("appointmentService");
    const appointmentDate = document.getElementById("appointmentDate");
    const appointmentTime = document.getElementById("appointmentTime");

    const appointmentServiceInfo = document.getElementById("appointmentServiceInfo");
    const appointmentDuration = document.getElementById("appointmentDuration");

    const appointmentFormMessage = document.getElementById("appointmentFormMessage");

    const addAppointmentButton = document.getElementById("addAppointmentButton");
    const closeAppointmentModal = document.getElementById("closeAppointmentModal");
    const cancelAppointmentButton = document.getElementById("cancelAppointmentButton");
    const saveAppointmentButton = document.getElementById("saveAppointmentButton");

    // =====================================================
    // VARIABLES
    // =====================================================

    let appointments = [];
    let services = [];

    // =====================================================
    // UTILIDADES
    // =====================================================

    function escaparHTML(valor) {
        return String(valor ?? "").replace(/[&<>"']/g, caracter => {
            const caracteres = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return caracteres[caracter];
        });
    }


    function obtenerFechaLocal() {
        const fecha = new Date();

        const anio = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, "0");
        const dia = String(fecha.getDate()).padStart(2, "0");

        return `${anio}-${mes}-${dia}`;
    }


    function formatearFecha(fecha) {
        if (!fecha) return "Sin fecha";

        const partes = String(fecha).split("-");

        if (partes.length !== 3) return fecha;

        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }


    function formatearHora(hora) {
        if (!hora) return "--:--";

        return String(hora).substring(0, 5);
    }


    function obtenerClaseEstado(estado) {
        const clases = {
            pendiente: "status-pending",
            confirmada: "status-confirmed",
            cancelada: "status-cancelled",
            completada: "status-completed"
        };

        return clases[estado] || "";
    }


    function obtenerTextoEstado(estado) {
        const textos = {
            pendiente: "Pendiente",
            confirmada: "Confirmada",
            cancelada: "Cancelada",
            completada: "Completada"
        };

        return textos[estado] || estado;
    }


    function mostrarError(mensaje) {
        appointmentsError.hidden = false;
        appointmentsErrorMessage.textContent = mensaje;
    }


    function ocultarError() {
        appointmentsError.hidden = true;
    }


    // =====================================================
    // VALIDAR SESIÓN
    // =====================================================

    async function validarSesion() {
        try {
            const respuesta = await window.API.get("/auth/validate");

            if (!respuesta.ok) {
                window.location.href = "/login";
                return false;
            }

            const datos = respuesta.data || {};

            // Datos del establecimiento
            const establecimiento = datos.establecimiento || {};

            // Nombre comercial del establecimiento
            const nombreEstablecimiento =
                establecimiento.nombre_comercial || "Establecimiento";

            // Datos del administrador
            const usuario = datos.usuario || {};

            const nombreAdministrador = [
                usuario.nombre,
                usuario.apellido
            ].filter(Boolean).join(" ") || "Administrador";

            // Actualizar encabezado
            establishmentName.textContent = nombreEstablecimiento;
            adminName.textContent = nombreAdministrador;

            userAvatar.textContent = nombreAdministrador
                .charAt(0)
                .toUpperCase();

            return true;

        } catch (error) {
            console.error("Error al validar sesión:", error);
            window.location.href = "/login";
            return false;
        }
    }


    // =====================================================
    // CERRAR SESIÓN
    // =====================================================

    logoutButton.addEventListener("click", async () => {
        try {
            await window.API.post("/auth/logout", {});
            window.location.href = "/";

        } catch (error) {
            console.error("Error al cerrar sesión:", error);
            alert(error.message || "No fue posible cerrar la sesión.");
        }
    });


    // =====================================================
    // CONSULTAR SERVICIOS
    // =====================================================

    async function cargarServicios() {
        try {
            const respuesta = await window.API.get("/services/");

            if (!respuesta.ok || !Array.isArray(respuesta.data)) {
                throw new Error("No fue posible consultar los servicios.");
            }

            services = respuesta.data;

            appointmentService.innerHTML = `
                <option value="">Selecciona un servicio</option>
            `;

            services
                .filter(servicio => Number(servicio.estado) === 1)
                .forEach(servicio => {
                    const opcion = document.createElement("option");

                    opcion.value = servicio.id_servicio;
                    opcion.textContent = servicio.nombre;

                    appointmentService.appendChild(opcion);
                });

        } catch (error) {
            console.error("Error al cargar servicios:", error);
        }
    }


// =====================================================
// CONSULTAR CLIENTES
// =====================================================

    async function cargarClientes() {
        try {
            appointmentClient.innerHTML = `
                <option value="">Cargando clientes...</option>
            `;

            const respuesta = await window.API.get("/clients/");

            if (!respuesta.ok || !Array.isArray(respuesta.data)) {
                throw new Error("No fue posible consultar los clientes.");
            }

            appointmentClient.innerHTML = `
                <option value="">Selecciona un cliente</option>
            `;

            respuesta.data.forEach(cliente => {
                const opcion = document.createElement("option");

                opcion.value = cliente.id_cliente;
                opcion.textContent = cliente.nombre;

                appointmentClient.appendChild(opcion);
            });

            if (respuesta.data.length === 0) {
                appointmentClient.innerHTML = `
                    <option value="">No hay clientes registrados</option>
                `;
            }

        } catch (error) {
            console.error("Error al cargar clientes:", error);

            appointmentClient.innerHTML = `
                <option value="">Error al cargar clientes</option>
            `;
        }
    }


    // =====================================================
    // INFORMACIÓN DEL SERVICIO SELECCIONADO
    // =====================================================

    appointmentService.addEventListener("change", () => {
        const idServicio = Number(appointmentService.value);

        const servicio = services.find(
            item => Number(item.id_servicio) === idServicio
        );

        if (!servicio) {
            appointmentServiceInfo.hidden = true;
            appointmentDuration.textContent = "0 minutos";
            return;
        }

        appointmentDuration.textContent =
            `${servicio.duracion_minutos} minutos`;

        appointmentServiceInfo.hidden = false;
    });


    // =====================================================
    // CONSULTAR CITAS
    // =====================================================

    async function cargarCitas() {
        loadingAppointments.hidden = false;
        emptyAppointments.hidden = true;
        appointmentsTableBody.innerHTML = "";

        ocultarError();

        try {
            const respuesta = await window.API.get("/appointments/");

            if (!respuesta.ok || !Array.isArray(respuesta.data)) {
                throw new Error("No fue posible obtener las citas.");
            }

            appointments = respuesta.data;

            actualizarEstadisticas();
            aplicarFiltros();

        } catch (error) {
            console.error("Error al consultar citas:", error);

            mostrarError(
                error.message || "No fue posible cargar las citas."
            );

        } finally {
            loadingAppointments.hidden = true;
        }
    }


    // =====================================================
    // ESTADÍSTICAS
    // =====================================================

    function actualizarEstadisticas() {
        totalAppointments.textContent = appointments.length;

        pendingAppointments.textContent = appointments.filter(
            cita => cita.estado === "pendiente"
        ).length;

        confirmedAppointments.textContent = appointments.filter(
            cita => cita.estado === "confirmada"
        ).length;
    }


    // =====================================================
    // FILTRAR CITAS
    // =====================================================

    function aplicarFiltros() {
        const fechaSeleccionada = filterDate.value;
        const estadoSeleccionado = filterStatus.value;

        let resultado = [...appointments];

        if (fechaSeleccionada) {
            resultado = resultado.filter(
                cita => String(cita.fecha).substring(0, 10) === fechaSeleccionada
            );
        }

        if (estadoSeleccionado !== "todos") {
            resultado = resultado.filter(
                cita => cita.estado === estadoSeleccionado
            );
        }

        renderizarCitas(resultado);
    }


    filterDate.addEventListener("change", aplicarFiltros);
    filterStatus.addEventListener("change", aplicarFiltros);


    clearFiltersButton.addEventListener("click", () => {
        filterDate.value = "";
        filterStatus.value = "todos";

        aplicarFiltros();
    });


    // =====================================================
    // RENDERIZAR CITAS
    // =====================================================

    function renderizarCitas(lista) {
        appointmentsTableBody.innerHTML = "";

        if (lista.length === 0) {
            emptyAppointments.hidden = false;
            return;
        }

        emptyAppointments.hidden = true;

        lista.forEach(cita => {
            const fila = document.createElement("tr");

            const nombreCliente = escaparHTML(
                cita.nombre_cliente || "Cliente"
            );

            const telefonoCliente = escaparHTML(
                cita.telefono_cliente || ""
            );

            const nombreServicio = escaparHTML(
                cita.nombre_servicio || "Servicio"
            );

            const fecha = escaparHTML(
                formatearFecha(cita.fecha)
            );

            const horaInicio = escaparHTML(
                formatearHora(cita.hora_inicio)
            );

            const horaFin = escaparHTML(
                formatearHora(cita.hora_fin)
            );

            const estado = escaparHTML(cita.estado);

            fila.innerHTML = `
                <td>
                    <div class="appointment-client">
                        <strong>${nombreCliente}</strong>
                        <span class="appointment-client-contact">
                            ${telefonoCliente}
                        </span>
                    </div>
                </td>

                <td>
                    <div class="appointment-service">
                        ${nombreServicio}
                    </div>
                </td>

                <td>
                    <div class="appointment-date">
                        ${fecha}
                    </div>
                </td>

                <td>
                    <div class="appointment-time">
                        ${horaInicio} - ${horaFin}
                    </div>
                </td>

                <td>
                    <span class="status-badge ${obtenerClaseEstado(estado)}">
                        ${obtenerTextoEstado(estado)}
                    </span>
                </td>

                <td>
                    <div class="appointment-actions">
                        ${obtenerBotonesAccion(cita)}
                    </div>
                </td>
            `;

            appointmentsTableBody.appendChild(fila);
        });
    }


    // =====================================================
    // BOTONES SEGÚN EL ESTADO
    // =====================================================

    function obtenerBotonesAccion(cita) {
        let botones = `
            <button
                type="button"
                class="action-button"
                data-action="detail"
                data-id="${cita.id_cita}"
                title="Consultar cita"
            >
                Ver
            </button>
        `;

        if (cita.estado === "pendiente") {
            botones += `
                <button
                    type="button"
                    class="action-button"
                    data-action="confirm"
                    data-id="${cita.id_cita}"
                >
                    Confirmar
                </button>

                <button
                    type="button"
                    class="action-button"
                    data-action="cancel"
                    data-id="${cita.id_cita}"
                >
                    Cancelar
                </button>
            `;
        }

        if (cita.estado === "confirmada") {
            botones += `
                <button
                    type="button"
                    class="action-button"
                    data-action="complete"
                    data-id="${cita.id_cita}"
                >
                    Completar
                </button>

                <button
                    type="button"
                    class="action-button"
                    data-action="cancel"
                    data-id="${cita.id_cita}"
                >
                    Cancelar
                </button>
            `;
        }

        return botones;
    }


    // =====================================================
    // ACCIONES DE LA TABLA
    // =====================================================

    appointmentsTableBody.addEventListener("click", async event => {
        const boton = event.target.closest("button[data-action]");

        if (!boton) return;

        const idCita = Number(boton.dataset.id);
        const accion = boton.dataset.action;

        const cita = appointments.find(
            item => Number(item.id_cita) === idCita
        );

        if (!cita) return;

        if (accion === "detail") {
            consultarDetalleCita(idCita);
            return;
        }

        const estados = {
            confirm: "confirmada",
            cancel: "cancelada",
            complete: "completada"
        };

        const nuevoEstado = estados[accion];

        if (!nuevoEstado) return;

        await cambiarEstadoCita(idCita, nuevoEstado);
    });


    // =====================================================
    // CONSULTAR DETALLE DE UNA CITA
    // =====================================================

    async function consultarDetalleCita(idCita) {
        try {
            const respuesta = await window.API.get(
                `/appointments/${idCita}`
            );

            if (!respuesta.ok || !respuesta.data) {
                throw new Error("No fue posible consultar la cita.");
            }

            const cita = respuesta.data;

            alert(
                `DETALLE DE LA CITA\n\n` +
                `Cliente: ${cita.nombre_cliente || "No disponible"}\n` +
                `Teléfono: ${cita.telefono_cliente || "No disponible"}\n` +
                `Servicio: ${cita.nombre_servicio || "No disponible"}\n` +
                `Fecha: ${formatearFecha(cita.fecha)}\n` +
                `Hora: ${formatearHora(cita.hora_inicio)} - ${formatearHora(cita.hora_fin)}\n` +
                `Duración: ${cita.duracion_minutos || "No disponible"} minutos\n` +
                `Precio: $${Number(cita.precio || 0).toLocaleString("es-CO")}\n` +
                `Estado: ${obtenerTextoEstado(cita.estado)}`
            );

        } catch (error) {
            console.error("Error al consultar detalle:", error);
            alert(error.message);
        }
    }


    // =====================================================
    // CAMBIAR ESTADO DE UNA CITA
    // =====================================================

    async function cambiarEstadoCita(idCita, nuevoEstado) {
        const mensajes = {
            confirmada: "¿Deseas confirmar esta cita?",
            cancelada: "¿Deseas cancelar esta cita?",
            completada: "¿Deseas marcar esta cita como completada?"
        };

        if (!confirm(mensajes[nuevoEstado])) return;

        try {
            const respuesta = await window.API.patch(
                `/appointments/${idCita}/status`,
                {
                    estado: nuevoEstado
                }
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible cambiar el estado."
                );
            }

            alert(respuesta.mensaje || "Estado actualizado correctamente.");

            await cargarCitas();

        } catch (error) {
            console.error("Error al cambiar estado:", error);
            alert(error.message);
        }
    }


    // =====================================================
    // ABRIR MODAL
    // =====================================================

    function abrirModal() {
        appointmentForm.reset();

        appointmentId.value = "";
        appointmentServiceInfo.hidden = true;

        appointmentFormMessage.hidden = true;
        appointmentFormMessage.textContent = "";

        document.getElementById("modalTitle").textContent = "Agendar cita";

        appointmentDate.min = obtenerFechaLocal();

        appointmentModal.hidden = false;
        appointmentModal.setAttribute("aria-hidden", "false");
    }


    // =====================================================
    // CERRAR MODAL
    // =====================================================

    function cerrarModal() {
        appointmentModal.hidden = true;
        appointmentModal.setAttribute("aria-hidden", "true");

        appointmentForm.reset();

        appointmentFormMessage.hidden = true;
        appointmentServiceInfo.hidden = true;
    }


    addAppointmentButton.addEventListener("click", abrirModal);

    closeAppointmentModal.addEventListener("click", cerrarModal);

    cancelAppointmentButton.addEventListener("click", cerrarModal);


    appointmentModal.addEventListener("click", event => {
        if (event.target === appointmentModal) {
            cerrarModal();
        }
    });


    // =====================================================
    // REGISTRAR CITA
    // =====================================================

    appointmentForm.addEventListener("submit", async event => {
        event.preventDefault();

        const datos = {
            id_cliente: Number(appointmentClient.value),
            id_servicio: Number(appointmentService.value),
            fecha: appointmentDate.value,
            hora_inicio: appointmentTime.value
        };

        if (
            !datos.id_cliente ||
            !datos.id_servicio ||
            !datos.fecha ||
            !datos.hora_inicio
        ) {
            mostrarMensajeFormulario(
                "Completa todos los campos obligatorios."
            );

            return;
        }

        const servicio = services.find(
            item => Number(item.id_servicio) === datos.id_servicio
        );

        if (!servicio) {
            mostrarMensajeFormulario(
                "Selecciona un servicio válido."
            );

            return;
        }

        saveAppointmentButton.disabled = true;
        saveAppointmentButton.textContent = "Guardando...";

        try {
            const respuesta = await window.API.post(
                "/appointments/",
                datos
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible registrar la cita."
                );
            }

            alert(respuesta.mensaje || "Cita registrada correctamente.");

            cerrarModal();

            await cargarCitas();

        } catch (error) {
            console.error("Error al registrar cita:", error);

            mostrarMensajeFormulario(error.message);

        } finally {
            saveAppointmentButton.disabled = false;
            saveAppointmentButton.textContent = "Guardar cita";
        }
    });


    // =====================================================
    // MENSAJES DEL FORMULARIO
    // =====================================================

    function mostrarMensajeFormulario(mensaje) {
        appointmentFormMessage.textContent = mensaje;
        appointmentFormMessage.hidden = false;
    }


    // =====================================================
    // REINTENTAR CARGA
    // =====================================================

    retryAppointmentsButton.addEventListener("click", cargarCitas);


    // =====================================================
    // INICIALIZACIÓN
    // =====================================================

    const sesionValida = await validarSesion();

    if (!sesionValida) return;

    await cargarClientes();
    await cargarServicios();
    await cargarCitas();

});
