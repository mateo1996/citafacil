
document.addEventListener("DOMContentLoaded", async () => {

    // =====================================================
    // ELEMENTOS DEL DOM
    // =====================================================

    const establishmentName = document.getElementById("establishmentName");
    const adminName = document.getElementById("adminName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const totalSchedules = document.getElementById("totalSchedules");
    const activeSchedules = document.getElementById("activeSchedules");
    const inactiveSchedules = document.getElementById("inactiveSchedules");

    const filterScheduleStatus = document.getElementById("filterScheduleStatus");

    const schedulesGrid = document.getElementById("schedulesGrid");
    const emptySchedules = document.getElementById("emptySchedules");
    const loadingSchedules = document.getElementById("loadingSchedules");
    const schedulesError = document.getElementById("schedulesError");
    const retrySchedulesButton = document.getElementById("retrySchedulesButton");

    const scheduleModal = document.getElementById("scheduleModal");
    const scheduleForm = document.getElementById("scheduleForm");

    const scheduleId = document.getElementById("scheduleId");
    const scheduleDay = document.getElementById("scheduleDay");
    const scheduleStart = document.getElementById("scheduleStart");
    const scheduleEnd = document.getElementById("scheduleEnd");

    const enableBreak = document.getElementById("enableBreak");
    const breakFields = document.getElementById("breakFields");
    const breakStart = document.getElementById("breakStart");
    const breakEnd = document.getElementById("breakEnd");

    const modalTitle = document.getElementById("modalTitle");
    const saveScheduleButton = document.getElementById("saveScheduleButton");
    const cancelScheduleButton = document.getElementById("cancelScheduleButton");
    const closeScheduleModal = document.getElementById("closeScheduleModal");

    const scheduleFormMessage = document.getElementById("scheduleFormMessage");

    // =====================================================
    // CONFIGURACIÓN
    // =====================================================

    const DIAS_SEMANA = [
        { valor: "lunes", nombre: "Lunes" },
        { valor: "martes", nombre: "Martes" },
        { valor: "miercoles", nombre: "Miércoles" },
        { valor: "jueves", nombre: "Jueves" },
        { valor: "viernes", nombre: "Viernes" },
        { valor: "sabado", nombre: "Sábado" },
        { valor: "domingo", nombre: "Domingo" }
    ];

    // =====================================================
    // ESTADO
    // =====================================================

    let horarios = [];
    let cargando = false;

    // =====================================================
    // VALIDAR API
    // =====================================================

    if (!window.API) {
        console.error("No se encontró la configuración de la API.");
        return;
    }

    // =====================================================
    // DATOS DEL ESTABLECIMIENTO
    // =====================================================

    function mostrarDatos(establecimiento) {

        const nombreComercial =
            establecimiento.nombre_comercial || "Establecimiento";

        const nombreResponsable =
            establecimiento.nombre || "Administrador";

        if (establishmentName) {
            establishmentName.textContent = nombreComercial;
        }

        if (adminName) {
            adminName.textContent = nombreResponsable;
        }

        if (userAvatar) {
            userAvatar.textContent =
                nombreComercial.charAt(0).toUpperCase();
        }
    }

    // =====================================================
    // VALIDAR SESIÓN
    // =====================================================

    async function validarSesion() {

        try {

            const respuesta = await window.API.get("/auth/validate");

            if (!respuesta.ok || !respuesta.data) {
                throw new Error("Sesión no válida.");
            }

            if (respuesta.data.tipo_cuenta !== "establecimiento") {
                throw new Error("La cuenta no corresponde a un establecimiento.");
            }

            const establecimiento = respuesta.data.establecimiento;

            if (!establecimiento) {
                throw new Error("No se encontraron los datos del establecimiento.");
            }

            mostrarDatos(establecimiento);

            return true;

        } catch (error) {

            console.error("Error al validar la sesión:", error);

            window.location.href = "/";
            return false;
        }
    }

    // =====================================================
    // CERRAR SESIÓN
    // =====================================================

    async function cerrarSesion() {

        try {

            await window.API.post("/auth/logout");

        } catch (error) {

            console.error("Error al cerrar sesión:", error);

        } finally {

            window.location.href = "/";
        }
    }

    if (logoutButton) {
        logoutButton.addEventListener("click", cerrarSesion);
    }

    // =====================================================
    // MENSAJES
    // =====================================================

    function mostrarMensajeFormulario(mensaje, tipo = "error") {

        if (!scheduleFormMessage) return;

        scheduleFormMessage.textContent = mensaje;
        scheduleFormMessage.className = `form-message ${tipo}`;
        scheduleFormMessage.hidden = false;
    }

    function limpiarMensajeFormulario() {

        if (!scheduleFormMessage) return;

        scheduleFormMessage.textContent = "";
        scheduleFormMessage.hidden = true;
        scheduleFormMessage.className = "form-message";
    }

    function mostrarErrorGeneral(mensaje) {

        if (!schedulesError) return;

        const texto = schedulesError.querySelector("p");

        if (texto) {
            texto.textContent = mensaje;
        }

        schedulesError.hidden = false;
    }

    // =====================================================
    // BUSCAR HORARIO POR DÍA
    // =====================================================

    function obtenerHorarioPorDia(dia) {

        return horarios.find(
            horario => horario.dia === dia
        );
    }

    // =====================================================
    // ACTUALIZAR ESTADÍSTICAS
    // =====================================================

    function actualizarEstadisticas() {

        const total = horarios.length;

        const activos = horarios.filter(
            horario => Number(horario.estado) === 1
        ).length;

        const inactivos = horarios.filter(
            horario => Number(horario.estado) === 0
        ).length;

        if (totalSchedules) {
            totalSchedules.textContent = total;
        }

        if (activeSchedules) {
            activeSchedules.textContent = activos;
        }

        if (inactiveSchedules) {
            inactiveSchedules.textContent = inactivos;
        }
    }

    // =====================================================
    // CREAR ELEMENTOS HTML
    // =====================================================

    function crearElemento(etiqueta, clase, texto = "") {

        const elemento = document.createElement(etiqueta);

        if (clase) {
            elemento.className = clase;
        }

        if (texto) {
            elemento.textContent = texto;
        }

        return elemento;
    }

    // =====================================================
    // CREAR BOTÓN
    // =====================================================

    function crearBoton(texto, clase, accion, titulo) {

        const boton = document.createElement("button");

        boton.type = "button";
        boton.textContent = texto;
        boton.className = clase;
        boton.title = titulo;
        boton.setAttribute("aria-label", titulo);

        boton.addEventListener("click", accion);

        return boton;
    }

    // =====================================================
    // MOSTRAR TARJETA SIN CONFIGURAR
    // =====================================================

    function crearTarjetaSinConfigurar(dia) {

        const tarjeta = crearElemento(
            "article",
            "schedule-card unconfigured"
        );

        const encabezado = crearElemento(
            "div",
            "schedule-card-header"
        );

        const nombreDia = crearElemento(
            "h3",
            "schedule-day",
            dia.nombre
        );

        const estado = crearElemento(
            "span",
            "schedule-status unconfigured",
            "Sin configurar"
        );

        encabezado.append(nombreDia, estado);

        const mensaje = crearElemento(
            "p",
            "schedule-empty",
            "Todavía no has registrado un horario para este día."
        );

        const boton = crearBoton(
            "+ Configurar horario",
            "add-schedule-button",
            () => abrirModalRegistro(dia.valor),
            `Configurar horario del ${dia.nombre}`
        );

        tarjeta.append(encabezado, mensaje, boton);

        return tarjeta;
    }

    // =====================================================
    // MOSTRAR TARJETA CONFIGURADA
    // =====================================================

    function crearTarjetaConfigurada(dia, horario) {

        const estadoActivo = Number(horario.estado) === 1;

        const tarjeta = crearElemento(
            "article",
            `schedule-card ${estadoActivo ? "active" : "inactive"}`
        );

        // ENCABEZADO

        const encabezado = crearElemento(
            "div",
            "schedule-card-header"
        );

        const nombreDia = crearElemento(
            "h3",
            "schedule-day",
            dia.nombre
        );

        const insignia = crearElemento(
            "span",
            `schedule-status ${estadoActivo ? "active" : "inactive"}`,
            estadoActivo ? "Activo" : "Inactivo"
        );

        encabezado.append(nombreDia, insignia);

        // HORARIO DE ATENCIÓN

        const informacionHoras = crearElemento(
            "div",
            "schedule-hours"
        );

        const etiquetaHoras = crearElemento(
            "p",
            "schedule-hours-label",
            "Horario de atención"
        );

        const horas = crearElemento(
            "p",
            "schedule-hours-value",
            `${horario.hora_inicio} – ${horario.hora_fin}`
        );

        informacionHoras.append(etiquetaHoras, horas);

        // DESCANSO

        let informacionDescanso;

        if (horario.hora_inicio_descanso && horario.hora_fin_descanso) {

            informacionDescanso = crearElemento(
                "div",
                "schedule-break"
            );

            const etiquetaDescanso = crearElemento(
                "p",
                "",
                "Horario de descanso"
            );

            const horasDescanso = crearElemento(
                "strong",
                "",
                `${horario.hora_inicio_descanso} – ${horario.hora_fin_descanso}`
            );

            informacionDescanso.append(
                etiquetaDescanso,
                horasDescanso
            );

        } else {

            informacionDescanso = crearElemento(
                "p",
                "schedule-no-break",
                "Sin horario de descanso"
            );
        }

        // ACCIONES

        const acciones = crearElemento(
            "div",
            "schedule-actions"
        );

        const botonEditar = crearBoton(
            "Editar",
            "edit-schedule-button",
            () => abrirModalEdicion(horario),
            `Editar horario del ${dia.nombre}`
        );

        const botonEstado = crearBoton(
            estadoActivo ? "Desactivar" : "Activar",
            "toggle-schedule-button",
            () => cambiarEstadoHorario(horario),
            estadoActivo
                ? `Desactivar horario del ${dia.nombre}`
                : `Activar horario del ${dia.nombre}`
        );

        acciones.append(botonEditar, botonEstado);

        tarjeta.append(
            encabezado,
            informacionHoras,
            informacionDescanso,
            acciones
        );

        return tarjeta;
    }

    // =====================================================
    // MOSTRAR LOS SIETE DÍAS
    // =====================================================

    function mostrarHorarios() {

        if (!schedulesGrid) return;

        schedulesGrid.replaceChildren();

        const filtro = filterScheduleStatus
            ? filterScheduleStatus.value
            : "todos";

        let diasMostrados = 0;

        DIAS_SEMANA.forEach(dia => {

            const horario = obtenerHorarioPorDia(dia.valor);

            const estaConfigurado = Boolean(horario);

            // FILTRO: SIN CONFIGURAR

            if (filtro === "pendientes" && estaConfigurado) {
                return;
            }

            // FILTRO: CONFIGURADOS

            if (filtro === "configurados" && !estaConfigurado) {
                return;
            }

            // FILTRO: ACTIVOS

            if (
                filtro === "1" &&
                (!estaConfigurado || Number(horario.estado) !== 1)
            ) {
                return;
            }

            // FILTRO: INACTIVOS

            if (
                filtro === "0" &&
                (!estaConfigurado || Number(horario.estado) !== 0)
            ) {
                return;
            }

            const tarjeta = estaConfigurado
                ? crearTarjetaConfigurada(dia, horario)
                : crearTarjetaSinConfigurar(dia);

            schedulesGrid.appendChild(tarjeta);

            diasMostrados++;
        });

        // MENSAJE CUANDO NO HAY RESULTADOS

        if (emptySchedules) {
            emptySchedules.hidden = diasMostrados !== 0;
        }
    }

    // =====================================================
    // FILTRAR HORARIOS
    // =====================================================

    if (filterScheduleStatus) {

        filterScheduleStatus.addEventListener(
            "change",
            mostrarHorarios
        );
    }

    // =====================================================
    // CONSULTAR HORARIOS
    // =====================================================

    async function cargarHorarios() {

        if (cargando) return;

        cargando = true;

        if (loadingSchedules) {
            loadingSchedules.hidden = false;
        }

        if (schedulesError) {
            schedulesError.hidden = true;
        }

        if (schedulesGrid) {
            schedulesGrid.hidden = true;
        }

        if (emptySchedules) {
            emptySchedules.hidden = true;
        }

        try {

            const respuesta = await window.API.get("/schedules/");

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible consultar los horarios."
                );
            }

            if (!Array.isArray(respuesta.data)) {
                throw new Error(
                    "El servidor devolvió una lista de horarios inválida."
                );
            }

            horarios = respuesta.data;

            actualizarEstadisticas();
            mostrarHorarios();

            if (schedulesGrid) {
                schedulesGrid.hidden = false;
            }

        } catch (error) {

            console.error("Error al consultar horarios:", error);

            mostrarErrorGeneral(error.message);

        } finally {

            cargando = false;

            if (loadingSchedules) {
                loadingSchedules.hidden = true;
            }
        }
    }

    // =====================================================
    // ABRIR MODAL
    // =====================================================

    function abrirModal() {

        if (!scheduleModal) return;

        limpiarMensajeFormulario();

        scheduleModal.hidden = false;
        scheduleModal.setAttribute("aria-hidden", "false");

        if (scheduleDay) {
            scheduleDay.focus();
        }
    }

    // =====================================================
    // CERRAR MODAL
    // =====================================================

    function cerrarModal() {

        if (!scheduleModal) return;

        scheduleModal.hidden = true;
        scheduleModal.setAttribute("aria-hidden", "true");

        if (scheduleForm) {
            scheduleForm.reset();
        }

        if (scheduleId) {
            scheduleId.value = "";
        }

        if (breakFields) {
            breakFields.hidden = true;
        }

        limpiarMensajeFormulario();
    }

    // =====================================================
    // MOSTRAR U OCULTAR DESCANSO
    // =====================================================

    function actualizarCamposDescanso() {

        const habilitado = enableBreak.checked;

        breakFields.hidden = !habilitado;

        breakStart.required = habilitado;
        breakEnd.required = habilitado;

        breakStart.disabled = !habilitado;
        breakEnd.disabled = !habilitado;

        if (!habilitado) {
            breakStart.value = "";
            breakEnd.value = "";
        }
    }

    if (enableBreak) {

        enableBreak.addEventListener(
            "change",
            actualizarCamposDescanso
        );
    }

    // =====================================================
    // PREPARAR FORMULARIO
    // =====================================================

    function prepararFormulario() {

        if (scheduleForm) {
            scheduleForm.reset();
        }

        if (scheduleId) {
            scheduleId.value = "";
        }

        if (breakFields) {
            breakFields.hidden = true;
        }

        if (breakStart) {
            breakStart.disabled = true;
            breakStart.required = false;
        }

        if (breakEnd) {
            breakEnd.disabled = true;
            breakEnd.required = false;
        }

        limpiarMensajeFormulario();
    }

    // =====================================================
    // REGISTRAR HORARIO
    // =====================================================

    function abrirModalRegistro(dia = "") {

        prepararFormulario();

        if (modalTitle) {
            modalTitle.textContent = "Configurar horario";
        }

        if (saveScheduleButton) {
            saveScheduleButton.textContent = "Guardar horario";
        }

        if (scheduleDay) {
            scheduleDay.value = dia;
        }

        abrirModal();
    }

    // =====================================================
    // EDITAR HORARIO
    // =====================================================

    function abrirModalEdicion(horario) {

        prepararFormulario();

        if (scheduleId) {
            scheduleId.value = horario.id_horario;
        }

        if (scheduleDay) {
            scheduleDay.value = horario.dia;
        }

        if (scheduleStart) {
            scheduleStart.value = horario.hora_inicio;
        }

        if (scheduleEnd) {
            scheduleEnd.value = horario.hora_fin;
        }

        const tieneDescanso =
            Boolean(horario.hora_inicio_descanso) &&
            Boolean(horario.hora_fin_descanso);

        if (enableBreak) {
            enableBreak.checked = tieneDescanso;
        }

        if (tieneDescanso) {

            breakFields.hidden = false;

            breakStart.disabled = false;
            breakEnd.disabled = false;

            breakStart.required = true;
            breakEnd.required = true;

            breakStart.value = horario.hora_inicio_descanso;
            breakEnd.value = horario.hora_fin_descanso;
        }

        if (modalTitle) {
            modalTitle.textContent = "Editar horario";
        }

        if (saveScheduleButton) {
            saveScheduleButton.textContent = "Guardar cambios";
        }

        abrirModal();
    }

    // =====================================================
    // VALIDAR FORMULARIO
    // =====================================================

    function obtenerDatosFormulario() {

        const dia = scheduleDay.value;
        const horaInicio = scheduleStart.value;
        const horaFin = scheduleEnd.value;

        if (!dia) {
            throw new Error("Debes seleccionar un día de la semana.");
        }

        if (!horaInicio || !horaFin) {
            throw new Error("Debes indicar la hora de apertura y cierre.");
        }

        if (horaInicio >= horaFin) {
            throw new Error(
                "La hora de apertura debe ser anterior a la hora de cierre."
            );
        }

        let horaInicioDescanso = null;
        let horaFinDescanso = null;

        if (enableBreak.checked) {

            horaInicioDescanso = breakStart.value;
            horaFinDescanso = breakEnd.value;

            if (!horaInicioDescanso || !horaFinDescanso) {
                throw new Error(
                    "Debes completar las dos horas del descanso."
                );
            }

            if (horaInicioDescanso >= horaFinDescanso) {
                throw new Error(
                    "El inicio del descanso debe ser anterior a su finalización."
                );
            }

            if (
                horaInicioDescanso <= horaInicio ||
                horaFinDescanso >= horaFin
            ) {
                throw new Error(
                    "El descanso debe estar dentro del horario de atención."
                );
            }
        }

        return {
            dia,
            hora_inicio: horaInicio,
            hora_fin: horaFin,
            hora_inicio_descanso: horaInicioDescanso,
            hora_fin_descanso: horaFinDescanso
        };
    }

    // =====================================================
    // GUARDAR HORARIO
    // =====================================================

    async function guardarHorario(evento) {

        evento.preventDefault();

        limpiarMensajeFormulario();

        let datos;

        try {

            datos = obtenerDatosFormulario();

        } catch (error) {

            mostrarMensajeFormulario(error.message);
            return;
        }

        const id = scheduleId ? scheduleId.value : "";

        const esEdicion = Boolean(id);

        try {

            if (saveScheduleButton) {
                saveScheduleButton.disabled = true;
                saveScheduleButton.textContent = "Guardando...";
            }

            let respuesta;

            if (esEdicion) {

                respuesta = await window.API.put(
                    `/schedules/${id}`,
                    datos
                );

            } else {

                respuesta = await window.API.post(
                    "/schedules/",
                    datos
                );
            }

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible guardar el horario."
                );
            }

            alert(
                respuesta.mensaje ||
                (
                    esEdicion
                        ? "Horario actualizado correctamente."
                        : "Horario registrado correctamente."
                )
            );

            cerrarModal();

            await cargarHorarios();

        } catch (error) {

            console.error("Error al guardar horario:", error);

            mostrarMensajeFormulario(error.message);

        } finally {

            if (saveScheduleButton) {

                saveScheduleButton.disabled = false;

                saveScheduleButton.textContent = esEdicion
                    ? "Guardar cambios"
                    : "Guardar horario";
            }
        }
    }

    // =====================================================
    // ACTIVAR / DESACTIVAR HORARIO
    // =====================================================

    async function cambiarEstadoHorario(horario) {

        const estadoActual = Number(horario.estado);

        const nuevoEstado = estadoActual === 1 ? 0 : 1;

        const accion = nuevoEstado === 1
            ? "activar"
            : "desactivar";

        const confirmar = window.confirm(
            `¿Estás seguro de que deseas ${accion} el horario del ${horario.dia}?`
        );

        if (!confirmar) return;

        try {

            const respuesta = await window.API.patch(
                `/schedules/${horario.id_horario}/status`,
                {
                    estado: nuevoEstado
                }
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible cambiar el estado del horario."
                );
            }

            alert(
                respuesta.mensaje || "Estado actualizado correctamente."
            );

            await cargarHorarios();

        } catch (error) {

            console.error("Error al cambiar estado del horario:", error);

            alert(error.message);
        }
    }

    // =====================================================
    // EVENTOS DEL MODAL
    // =====================================================

    if (closeScheduleModal) {
        closeScheduleModal.addEventListener("click", cerrarModal);
    }

    if (cancelScheduleButton) {
        cancelScheduleButton.addEventListener("click", cerrarModal);
    }

    if (scheduleForm) {
        scheduleForm.addEventListener("submit", guardarHorario);
    }

    if (scheduleModal) {

        scheduleModal.addEventListener("click", evento => {

            if (evento.target === scheduleModal) {
                cerrarModal();
            }
        });
    }

    document.addEventListener("keydown", evento => {

        if (
            evento.key === "Escape" &&
            scheduleModal &&
            !scheduleModal.hidden
        ) {
            cerrarModal();
        }
    });

    // =====================================================
    // REINTENTAR CONSULTA
    // =====================================================

    if (retrySchedulesButton) {
        retrySchedulesButton.addEventListener("click", cargarHorarios);
    }

    // =====================================================
    // INICIALIZACIÓN
    // =====================================================

    const sesionValida = await validarSesion();

    if (sesionValida) {
        await cargarHorarios();
    }

});
