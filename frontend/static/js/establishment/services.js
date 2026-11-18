
document.addEventListener("DOMContentLoaded", async () => {

    // =====================================================
    // ELEMENTOS DEL DOM
    // =====================================================

    const establishmentName = document.getElementById("establishmentName");
    const adminName = document.getElementById("adminName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const totalServices = document.getElementById("totalServices");
    const activeServices = document.getElementById("activeServices");
    const inactiveServices = document.getElementById("inactiveServices");

    const searchService = document.getElementById("searchService");
    const filterStatus = document.getElementById("filterStatus");

    const servicesTableBody = document.getElementById("servicesTableBody");
    const emptyServices = document.getElementById("emptyServices");
    const loadingServices = document.getElementById("loadingServices");
    const servicesError = document.getElementById("servicesError");
    const retryServicesButton = document.getElementById("retryServicesButton");

    const serviceModal = document.getElementById("serviceModal");
    const serviceForm = document.getElementById("serviceForm");
    const serviceId = document.getElementById("serviceId");
    const serviceName = document.getElementById("serviceName");
    const serviceDescription = document.getElementById("serviceDescription");
    const serviceDuration = document.getElementById("serviceDuration");
    const servicePrice = document.getElementById("servicePrice");

    const modalTitle = document.getElementById("modalTitle");
    const saveServiceButton = document.getElementById("saveServiceButton");
    const cancelServiceButton = document.getElementById("cancelServiceButton");
    const closeServiceModal = document.getElementById("closeServiceModal");
    const serviceFormMessage = document.getElementById("serviceFormMessage");

    const addServiceButton = document.getElementById("addServiceButton");

    // =====================================================
    // ESTADO
    // =====================================================

    let servicios = [];
    let cargando = false;

    // =====================================================
    // VALIDAR ELEMENTOS Y API
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

        if (!serviceFormMessage) return;

        serviceFormMessage.textContent = mensaje;
        serviceFormMessage.className = `form-message ${tipo}`;
        serviceFormMessage.hidden = false;
    }

    function limpiarMensajeFormulario() {

        if (!serviceFormMessage) return;

        serviceFormMessage.textContent = "";
        serviceFormMessage.hidden = true;
        serviceFormMessage.className = "form-message";
    }

    function mostrarErrorGeneral(mensaje) {

        if (servicesError) {
            servicesError.textContent = mensaje;
            servicesError.hidden = false;
        }
    }

    // =====================================================
    // FORMATO DE PRECIO
    // =====================================================

    function formatearPrecio(precio) {

        const valor = Number(precio);

        if (!Number.isFinite(valor)) {
            return "$0";
        }

        return new Intl.NumberFormat("es-CO", {
            style: "currency",
            currency: "COP",
            maximumFractionDigits: 0
        }).format(valor);
    }

    // =====================================================
    // ACTUALIZAR ESTADÍSTICAS
    // =====================================================

    function actualizarEstadisticas() {

        const total = servicios.length;

        const activos = servicios.filter(
            servicio => Number(servicio.estado) === 1
        ).length;

        const inactivos = servicios.filter(
            servicio => Number(servicio.estado) === 0
        ).length;

        if (totalServices) totalServices.textContent = total;
        if (activeServices) activeServices.textContent = activos;
        if (inactiveServices) inactiveServices.textContent = inactivos;
    }

    // =====================================================
    // CREAR CELDA
    // =====================================================

    function crearCelda(texto, clase = "") {

        const celda = document.createElement("td");

        celda.textContent = texto;

        if (clase) {
            celda.className = clase;
        }

        return celda;
    }

    // =====================================================
    // CREAR BOTÓN DE ACCIÓN
    // =====================================================

    function crearBoton(texto, clase, accion, titulo) {

        const boton = document.createElement("button");

        boton.type = "button";
        boton.textContent = texto;
        boton.className = `action-button ${clase}`;
        boton.title = titulo;
        boton.setAttribute("aria-label", titulo);

        boton.addEventListener("click", accion);

        return boton;
    }

    // =====================================================
    // MOSTRAR SERVICIOS
    // =====================================================

    function mostrarServicios(lista) {

        if (!servicesTableBody) return;

        servicesTableBody.replaceChildren();

        if (lista.length === 0) {

            if (emptyServices) {
                emptyServices.hidden = false;
            }

            return;
        }

        if (emptyServices) {
            emptyServices.hidden = true;
        }

        lista.forEach(servicio => {

            const fila = document.createElement("tr");

            const nombre = servicio.nombre || "Sin nombre";
            const descripcion = servicio.descripcion || "Sin descripción";
            const duracion = Number(servicio.duracion_minutos);
            const estado = Number(servicio.estado);

            fila.appendChild(crearCelda(nombre));
            fila.appendChild(crearCelda(descripcion));

            fila.appendChild(
                crearCelda(
                    Number.isFinite(duracion) ? `${duracion} minutos` : "No disponible"
                )
            );

            fila.appendChild(
                crearCelda(formatearPrecio(servicio.precio))
            );

            const celdaEstado = document.createElement("td");
            const insignia = document.createElement("span");

            insignia.className = estado === 1
                ? "status-badge status-active"
                : "status-badge status-inactive";

            insignia.textContent = estado === 1 ? "Activo" : "Inactivo";

            celdaEstado.appendChild(insignia);
            fila.appendChild(celdaEstado);

            const celdaAcciones = document.createElement("td");
            celdaAcciones.className = "actions-cell";

            celdaAcciones.appendChild(
                crearBoton(
                    "Ver",
                    "view",
                    () => consultarServicio(servicio.id_servicio),
                    "Consultar servicio"
                )
            );

            celdaAcciones.appendChild(
                crearBoton(
                    "Editar",
                    "edit",
                    () => abrirModalEdicion(servicio),
                    "Editar servicio"
                )
            );

            celdaAcciones.appendChild(
                crearBoton(
                    estado === 1 ? "Desactivar" : "Activar",
                    estado === 1 ? "deactivate" : "activate",
                    () => cambiarEstadoServicio(servicio),
                    estado === 1 ? "Desactivar servicio" : "Activar servicio"
                )
            );

            fila.appendChild(celdaAcciones);

            servicesTableBody.appendChild(fila);
        });
    }

    // =====================================================
    // BUSCAR Y FILTRAR
    // =====================================================

    function aplicarFiltros() {

        const busqueda = searchService
            ? searchService.value.trim().toLowerCase()
            : "";

        const estadoSeleccionado = filterStatus
            ? filterStatus.value
            : "todos";

        const resultado = servicios.filter(servicio => {

            const nombre = (servicio.nombre || "").toLowerCase();
            const descripcion = (servicio.descripcion || "").toLowerCase();

            const coincideBusqueda =
                nombre.includes(busqueda) ||
                descripcion.includes(busqueda);

            const coincideEstado =
                estadoSeleccionado === "todos" ||
                Number(servicio.estado) === Number(estadoSeleccionado);

            return coincideBusqueda && coincideEstado;
        });

        mostrarServicios(resultado);
    }

    if (searchService) {
        searchService.addEventListener("input", aplicarFiltros);
    }

    if (filterStatus) {
        filterStatus.addEventListener("change", aplicarFiltros);
    }

    // =====================================================
    // CONSULTAR SERVICIOS
    // =====================================================

    async function cargarServicios() {

        if (cargando) return;

        cargando = true;

        if (loadingServices) loadingServices.hidden = false;
        if (servicesError) servicesError.hidden = true;
        if (emptyServices) emptyServices.hidden = true;

        try {

            const respuesta = await window.API.get("/services/");

            if (!respuesta.ok) {
                throw new Error(respuesta.mensaje || "No fue posible consultar los servicios.");
            }

            if (!Array.isArray(respuesta.data)) {
                throw new Error("El servidor devolvió una lista de servicios inválida.");
            }

            servicios = respuesta.data;

            actualizarEstadisticas();
            aplicarFiltros();

        } catch (error) {

            console.error("Error al consultar servicios:", error);

            mostrarErrorGeneral(error.message);

        } finally {

            cargando = false;

            if (loadingServices) {
                loadingServices.hidden = true;
            }
        }
    }

    // =====================================================
    // CONSULTAR UN SERVICIO
    // =====================================================

    async function consultarServicio(id) {

        try {

            const respuesta = await window.API.get(`/services/${id}`);

            if (!respuesta.ok || !respuesta.data) {
                throw new Error(respuesta.mensaje || "No fue posible consultar el servicio.");
            }

            const servicio = respuesta.data;

            alert(
                `Nombre: ${servicio.nombre}\n` +
                `Descripción: ${servicio.descripcion || "Sin descripción"}\n` +
                `Duración: ${servicio.duracion_minutos} minutos\n` +
                `Precio: ${formatearPrecio(servicio.precio)}\n` +
                `Estado: ${Number(servicio.estado) === 1 ? "Activo" : "Inactivo"}`
            );

        } catch (error) {

            console.error("Error al consultar servicio:", error);

            alert(error.message);
        }
    }

    // =====================================================
    // ABRIR MODAL
    // =====================================================

    function abrirModal() {

        if (!serviceModal) return;

        limpiarMensajeFormulario();

        serviceModal.hidden = false;
        serviceModal.setAttribute("aria-hidden", "false");

        if (serviceName) {
            serviceName.focus();
        }
    }

    function cerrarModal() {

        if (!serviceModal) return;

        serviceModal.hidden = true;
        serviceModal.setAttribute("aria-hidden", "true");

        if (serviceForm) {
            serviceForm.reset();
        }

        if (serviceId) {
            serviceId.value = "";
        }

        limpiarMensajeFormulario();
    }

    // =====================================================
    // REGISTRAR SERVICIO
    // =====================================================

    function abrirModalRegistro() {

        if (!serviceForm) return;

        serviceForm.reset();

        if (serviceId) {
            serviceId.value = "";
        }

        if (modalTitle) {
            modalTitle.textContent = "Agregar servicio";
        }

        if (saveServiceButton) {
            saveServiceButton.textContent = "Guardar servicio";
        }

        abrirModal();
    }

    // =====================================================
    // EDITAR SERVICIO
    // =====================================================

    function abrirModalEdicion(servicio) {

        if (!serviceForm) return;

        serviceForm.reset();

        if (serviceId) serviceId.value = servicio.id_servicio;
        if (serviceName) serviceName.value = servicio.nombre || "";
        if (serviceDescription) serviceDescription.value = servicio.descripcion || "";
        if (serviceDuration) serviceDuration.value = servicio.duracion_minutos || "";
        if (servicePrice) servicePrice.value = servicio.precio ?? 0;

        if (modalTitle) {
            modalTitle.textContent = "Editar servicio";
        }

        if (saveServiceButton) {
            saveServiceButton.textContent = "Guardar cambios";
        }

        abrirModal();
    }

    // =====================================================
    // VALIDAR FORMULARIO
    // =====================================================

    function obtenerDatosFormulario() {

        const nombre = serviceName.value.trim();
        const descripcion = serviceDescription.value.trim();
        const duracion = Number(serviceDuration.value);
        const precio = Number(servicePrice.value);

        if (!nombre) {
            throw new Error("El nombre del servicio es obligatorio.");
        }

        if (nombre.length > 100) {
            throw new Error("El nombre no puede superar los 100 caracteres.");
        }

        if (!Number.isInteger(duracion) || duracion <= 0) {
            throw new Error("La duración debe ser un número entero mayor que cero.");
        }

        if (!Number.isFinite(precio) || precio < 0) {
            throw new Error("El precio debe ser un número mayor o igual a cero.");
        }

        return {
            nombre,
            descripcion,
            duracion_minutos: duracion,
            precio
        };
    }

    // =====================================================
    // GUARDAR SERVICIO
    // =====================================================

    async function guardarServicio(evento) {

        evento.preventDefault();

        limpiarMensajeFormulario();

        let datos;

        try {

            datos = obtenerDatosFormulario();

        } catch (error) {

            mostrarMensajeFormulario(error.message);
            return;
        }

        const id = serviceId ? serviceId.value : "";

        const esEdicion = Boolean(id);

        try {

            if (saveServiceButton) {
                saveServiceButton.disabled = true;
                saveServiceButton.textContent = "Guardando...";
            }

            let respuesta;

            if (esEdicion) {

                respuesta = await window.API.put(
                    `/services/${id}`,
                    datos
                );

            } else {

                respuesta = await window.API.post(
                    "/services/",
                    datos
                );
            }

            if (!respuesta.ok) {
                throw new Error(respuesta.mensaje || "No fue posible guardar el servicio.");
            }

            alert(
                respuesta.mensaje ||
                (esEdicion
                    ? "Servicio actualizado correctamente."
                    : "Servicio registrado correctamente.")
            );

            cerrarModal();
            await cargarServicios();

        } catch (error) {

            console.error("Error al guardar servicio:", error);

            mostrarMensajeFormulario(error.message);

        } finally {

            if (saveServiceButton) {
                saveServiceButton.disabled = false;
                saveServiceButton.textContent = esEdicion
                    ? "Guardar cambios"
                    : "Guardar servicio";
            }
        }
    }

    // =====================================================
    // ACTIVAR / DESACTIVAR SERVICIO
    // =====================================================

    async function cambiarEstadoServicio(servicio) {

        const estadoActual = Number(servicio.estado);
        const nuevoEstado = estadoActual === 1 ? 0 : 1;

        const accion = nuevoEstado === 1 ? "activar" : "desactivar";

        const confirmar = window.confirm(
            `¿Estás seguro de que deseas ${accion} el servicio "${servicio.nombre}"?`
        );

        if (!confirmar) return;

        try {

            const respuesta = await window.API.patch(
                `/services/${servicio.id_servicio}/status`,
                {
                    estado: nuevoEstado
                }
            );

            if (!respuesta.ok) {
                throw new Error(respuesta.mensaje || "No fue posible cambiar el estado.");
            }

            alert(respuesta.mensaje || "Estado actualizado correctamente.");

            await cargarServicios();

        } catch (error) {

            console.error("Error al cambiar estado:", error);

            alert(error.message);
        }
    }

    // =====================================================
    // EVENTOS DEL MODAL
    // =====================================================

    if (addServiceButton) {
        addServiceButton.addEventListener("click", abrirModalRegistro);
    }

    if (closeServiceModal) {
        closeServiceModal.addEventListener("click", cerrarModal);
    }

    if (cancelServiceButton) {
        cancelServiceButton.addEventListener("click", cerrarModal);
    }

    if (serviceForm) {
        serviceForm.addEventListener("submit", guardarServicio);
    }

    if (serviceModal) {

        serviceModal.addEventListener("click", evento => {

            if (evento.target === serviceModal) {
                cerrarModal();
            }
        });
    }

    document.addEventListener("keydown", evento => {

        if (evento.key === "Escape" && serviceModal && !serviceModal.hidden) {
            cerrarModal();
        }
    });

    // =====================================================
    // REINTENTAR CONSULTA
    // =====================================================

    if (retryServicesButton) {
        retryServicesButton.addEventListener("click", cargarServicios);
    }

    // =====================================================
    // INICIALIZACIÓN
    // =====================================================

    const sesionValida = await validarSesion();

    if (sesionValida) {
        await cargarServicios();
    }

});
