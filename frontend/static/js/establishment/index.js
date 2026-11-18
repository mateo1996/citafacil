
document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // 1. ELEMENTOS DEL DOM
    // =====================================================

    const establishmentName = document.getElementById("establishmentName");
    const adminName = document.getElementById("adminName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const totalAppointments = document.getElementById("totalAppointments");
    const pendingAppointments = document.getElementById("pendingAppointments");
    const totalClients = document.getElementById("totalClients");
    const totalServices = document.getElementById("totalServices");

    const upcomingAppointments = document.getElementById("upcomingAppointments");

    const calendarMonth = document.getElementById("calendarMonth");
    const calendarDays = document.getElementById("calendarDays");

    const previousMonthButton = document.getElementById("previousMonthButton");
    const nextMonthButton = document.getElementById("nextMonthButton");
    const todayButton = document.getElementById("todayButton");

    const selectedDateText = document.getElementById("selectedDateText");
    const selectedDayAppointments = document.getElementById("selectedDayAppointments");


    // =====================================================
    // 2. VARIABLES
    // =====================================================

    let todasLasCitas = [];

    const fechaActual = new Date();

    let fechaCalendario = new Date(
        fechaActual.getFullYear(),
        fechaActual.getMonth(),
        1
    );

    let fechaSeleccionada = obtenerFechaISO(fechaActual);

    const nombresMeses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];

    const nombresDias = [
        "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"
    ];


    // =====================================================
    // 3. UTILIDADES
    // =====================================================

    function obtenerFechaISO(fecha) {

        const anio = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, "0");
        const dia = String(fecha.getDate()).padStart(2, "0");

        return `${anio}-${mes}-${dia}`;
    }


    function convertirFechaLocal(fechaISO) {

        if (!fechaISO) return new Date(NaN);

        const [anio, mes, dia] = fechaISO.split("-").map(Number);

        return new Date(anio, mes - 1, dia);
    }


    function formatearFecha(fechaISO) {

        return convertirFechaLocal(fechaISO).toLocaleDateString("es-CO", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });
    }


    function formatearFechaCompleta(fechaISO) {

        const fecha = convertirFechaLocal(fechaISO);

        const texto = fecha.toLocaleDateString("es-CO", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        });

        return texto.charAt(0).toUpperCase() + texto.slice(1);
    }


    function escaparHTML(valor) {

        return String(valor ?? "").replace(/[&<>"']/g, caracter => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[caracter]);
    }


    function normalizarArray(respuesta) {

        return Array.isArray(respuesta?.data)
            ? respuesta.data
            : [];
    }


    function mostrarMensaje(contenedor, mensaje) {

        if (!contenedor) return;

        contenedor.innerHTML = `
            <div class="empty-state">
                ${escaparHTML(mensaje)}
            </div>
        `;
    }


    // =====================================================
    // 4. VALIDAR SESIÓN
    // =====================================================

    async function validarSesion() {

        try {

            const respuesta = await API.get("/auth/validate");

            const datos = respuesta.data || {};

            const establecimiento = datos.establecimiento || {};
            const usuario = datos.usuario || {};

            const nombreComercial =
                establecimiento.nombre_comercial || "Establecimiento";

            const nombreAdministrador = [
                usuario.nombre,
                usuario.apellido
            ]
                .filter(Boolean)
                .join(" ") || "Administrador";


            // Nombre comercial en el sidebar

            if (establishmentName) {
                establishmentName.textContent = nombreComercial;
            }


            // Nombre del administrador en el topbar

            if (adminName) {
                adminName.textContent = nombreAdministrador;
            }


            // Inicial del administrador

            if (userAvatar) {
                userAvatar.textContent =
                    nombreAdministrador.charAt(0).toUpperCase();
            }

            return true;

        } catch (error) {

            console.error("Error validando sesión:", error);

            window.location.href = "/login";

            return false;
        }
    }


    // =====================================================
    // 5. CERRAR SESIÓN
    // =====================================================

    if (logoutButton) {

        logoutButton.addEventListener("click", async () => {

            logoutButton.disabled = true;

            try {

                await API.post("/auth/logout", {});

                window.location.href = "/";

            } catch (error) {

                console.error("Error cerrando sesión:", error);

                alert("No fue posible cerrar la sesión.");

                logoutButton.disabled = false;
            }

        });

    }


    // =====================================================
    // 6. CARGAR ESTADÍSTICAS
    // =====================================================

    async function cargarEstadisticas() {

        // Cada consulta se ejecuta independientemente.

        await Promise.all([

            cargarTotalCitas(),

            cargarTotalClientes(),

            cargarTotalServicios()

        ]);

    }


    // -----------------------------------------------------
    // TOTAL DE CITAS
    // -----------------------------------------------------

    async function cargarTotalCitas() {

        try {

            const respuesta = await API.get("/appointments/");

            const citas = normalizarArray(respuesta);

            if (totalAppointments) {
                totalAppointments.textContent = citas.length;
            }

            if (pendingAppointments) {

                const pendientes = citas.filter(
                    cita => cita.estado === "pendiente"
                );

                pendingAppointments.textContent = pendientes.length;
            }

        } catch (error) {

            console.error("Error cargando total de citas:", error);

        }
    }


    // -----------------------------------------------------
    // TOTAL DE CLIENTES
    // -----------------------------------------------------

    async function cargarTotalClientes() {

        try {

            const respuesta = await API.get("/clients/");

            const clientes = normalizarArray(respuesta);

            if (totalClients) {
                totalClients.textContent = clientes.length;
            }

        } catch (error) {

            console.error("Error cargando total de clientes:", error);

        }
    }


    // -----------------------------------------------------
    // TOTAL DE SERVICIOS
    // -----------------------------------------------------

    async function cargarTotalServicios() {

        try {

            const respuesta = await API.get("/services/");

            const servicios = normalizarArray(respuesta);

            const serviciosActivos = servicios.filter(
                servicio => Number(servicio.estado) === 1
            );

            if (totalServices) {
                totalServices.textContent = serviciosActivos.length;
            }

        } catch (error) {

            console.error("Error cargando total de servicios:", error);

        }
    }


    // =====================================================
    // 7. PRÓXIMAS CITAS
    // =====================================================

    async function cargarProximasCitas() {

        if (!upcomingAppointments) return;

        try {

            upcomingAppointments.innerHTML = `
                <div class="loading-state">
                    Cargando próximas citas...
                </div>
            `;

            const respuesta = await API.get(
                "/appointments/upcoming?limite=5"
            );

            const citas = normalizarArray(respuesta);

            mostrarProximasCitas(citas);

        } catch (error) {

            console.error("Error cargando próximas citas:", error);

            mostrarMensaje(
                upcomingAppointments,
                "No fue posible cargar las próximas citas."
            );

        }
    }


    function mostrarProximasCitas(citas) {

        if (!upcomingAppointments) return;

        if (!citas.length) {

            mostrarMensaje(
                upcomingAppointments,
                "No tienes próximas citas."
            );

            return;
        }

        upcomingAppointments.innerHTML = citas.map(cita => `

            <div class="upcoming-appointment">

                <div class="upcoming-appointment-main">

                    <div class="upcoming-appointment-date">

                        ${escaparHTML(formatearFecha(cita.fecha))}

                        ${escaparHTML(cita.hora_inicio)}
                        -
                        ${escaparHTML(cita.hora_fin)}

                    </div>

                    <h4>
                        ${escaparHTML(cita.nombre_cliente)}
                    </h4>

                </div>


                <div class="upcoming-appointment-footer">

                    <span class="upcoming-appointment-service">
                        ${escaparHTML(cita.nombre_servicio)}
                    </span>

                    <span class="status-badge ${escaparHTML(cita.estado)}">
                        ${escaparHTML(cita.estado)}
                    </span>

                </div>

            </div>

        `).join("");

    }


    // =====================================================
    // 8. CARGAR CITAS DEL CALENDARIO
    // =====================================================

    async function cargarCitasCalendario() {

        try {

            if (calendarDays) {

                calendarDays.innerHTML = `
                    <div class="loading-state">
                        Cargando calendario...
                    </div>
                `;

            }

            const respuesta = await API.get("/appointments/");

            todasLasCitas = normalizarArray(respuesta);

            renderizarCalendario();

            mostrarCitasDelDia(fechaSeleccionada);

        } catch (error) {

            console.error("Error cargando calendario:", error);

            if (calendarDays) {

                mostrarMensaje(
                    calendarDays,
                    "No fue posible cargar el calendario."
                );

            }

            if (selectedDayAppointments) {

                mostrarMensaje(
                    selectedDayAppointments,
                    "No fue posible consultar las citas."
                );

            }

        }
    }


    // =====================================================
    // 9. OBTENER CITAS DE UNA FECHA
    // =====================================================

    function obtenerCitasPorFecha(fechaISO) {

        return todasLasCitas

            .filter(cita => cita.fecha === fechaISO)

            .sort((a, b) =>
                String(a.hora_inicio).localeCompare(
                    String(b.hora_inicio)
                )
            );

    }


    // =====================================================
    // 10. RENDERIZAR CALENDARIO
    // =====================================================

    function renderizarCalendario() {

        if (!calendarDays || !calendarMonth) return;

        const anio = fechaCalendario.getFullYear();
        const mes = fechaCalendario.getMonth();

        calendarMonth.textContent =
            `${nombresMeses[mes]} ${anio}`;

        calendarDays.innerHTML = "";


        // Encabezados de los días

        nombresDias.forEach(dia => {

            const elemento = document.createElement("div");

            elemento.className = "calendar-weekday";
            elemento.textContent = dia;

            calendarDays.appendChild(elemento);

        });


        // Primer y último día del mes

        const primerDia = new Date(anio, mes, 1);
        const ultimoDia = new Date(anio, mes + 1, 0);

        let desplazamiento = primerDia.getDay();

        desplazamiento = desplazamiento === 0
            ? 6
            : desplazamiento - 1;

        const totalCeldas = Math.ceil(
            (desplazamiento + ultimoDia.getDate()) / 7
        ) * 7;


        // Generar días

        for (let i = 0; i < totalCeldas; i++) {

            const numeroDia = i - desplazamiento + 1;

            const fecha = new Date(anio, mes, numeroDia);

            const fechaISO = obtenerFechaISO(fecha);

            const perteneceMes = fecha.getMonth() === mes;

            const citasDia = obtenerCitasPorFecha(fechaISO);


            // Crear botón

            const elemento = document.createElement("button");

            elemento.type = "button";
            elemento.className = "calendar-day";

            elemento.textContent = fecha.getDate();


            // Día de otro mes

            if (!perteneceMes) {
                elemento.classList.add("other-month");
            }


            // Día actual

            if (fechaISO === obtenerFechaISO(new Date())) {
                elemento.classList.add("today");
            }


            // Día seleccionado

            if (fechaISO === fechaSeleccionada) {
                elemento.classList.add("selected");
            }


            // Indicadores de citas

            if (citasDia.length > 0) {

                elemento.classList.add("has-appointments");

                const indicadores = document.createElement("div");

                indicadores.className = "calendar-indicators";


                // Estados únicos de las citas del día

                const estados = [
                    ...new Set(
                        citasDia.map(cita => cita.estado)
                    )
                ];

                estados.forEach(estado => {

                    const punto = document.createElement("span");

                    punto.className = `calendar-dot ${estado}`;

                    indicadores.appendChild(punto);

                });

                elemento.appendChild(indicadores);

            }


            // Seleccionar fecha

            elemento.addEventListener("click", () => {

                fechaSeleccionada = fechaISO;

                // Si se selecciona un día de otro mes,
                // cambiar también el mes del calendario.

                if (!perteneceMes) {

                    fechaCalendario = new Date(
                        fecha.getFullYear(),
                        fecha.getMonth(),
                        1
                    );

                }

                renderizarCalendario();

                mostrarCitasDelDia(fechaSeleccionada);

            });


            calendarDays.appendChild(elemento);

        }

    }


    // =====================================================
    // 11. MOSTRAR CITAS DEL DÍA SELECCIONADO
    // =====================================================

    function mostrarCitasDelDia(fechaISO) {

        if (!selectedDayAppointments) return;


        // Actualizar fecha del encabezado

        if (selectedDateText) {

            selectedDateText.textContent =
                formatearFechaCompleta(fechaISO);

        }


        const citasDia = obtenerCitasPorFecha(fechaISO);


        // Sin citas

        if (!citasDia.length) {

            mostrarMensaje(
                selectedDayAppointments,
                "No hay citas programadas para este día."
            );

            return;
        }


        // Mostrar citas

        selectedDayAppointments.innerHTML = citasDia.map(cita => `

            <div class="selected-day-appointment">

                <div class="selected-day-appointment-info">

                    <strong>
                        ${escaparHTML(cita.hora_inicio)}
                        -
                        ${escaparHTML(cita.hora_fin)}
                    </strong>

                    <h4>
                        ${escaparHTML(cita.nombre_cliente)}
                    </h4>

                    <span>
                        ${escaparHTML(cita.nombre_servicio)}
                    </span>

                </div>


                <span class="status-badge ${escaparHTML(cita.estado)}">
                    ${escaparHTML(cita.estado)}
                </span>

            </div>

        `).join("");

    }


    // =====================================================
    // 12. NAVEGACIÓN DEL CALENDARIO
    // =====================================================

    if (previousMonthButton) {

        previousMonthButton.addEventListener("click", () => {

            fechaCalendario = new Date(
                fechaCalendario.getFullYear(),
                fechaCalendario.getMonth() - 1,
                1
            );

            renderizarCalendario();

        });

    }


    if (nextMonthButton) {

        nextMonthButton.addEventListener("click", () => {

            fechaCalendario = new Date(
                fechaCalendario.getFullYear(),
                fechaCalendario.getMonth() + 1,
                1
            );

            renderizarCalendario();

        });

    }


    if (todayButton) {

        todayButton.addEventListener("click", () => {

            const hoy = new Date();

            fechaCalendario = new Date(
                hoy.getFullYear(),
                hoy.getMonth(),
                1
            );

            fechaSeleccionada = obtenerFechaISO(hoy);

            renderizarCalendario();

            mostrarCitasDelDia(fechaSeleccionada);

        });

    }


    // =====================================================
    // 13. INICIALIZAR DASHBOARD
    // =====================================================

    async function inicializarDashboard() {

        const sesionValida = await validarSesion();

        if (!sesionValida) return;

        await Promise.all([

            cargarEstadisticas(),

            cargarProximasCitas(),

            cargarCitasCalendario()

        ]);

    }


    inicializarDashboard();

});
