
document.addEventListener("DOMContentLoaded", async () => {

    // =====================================================
    // ELEMENTOS DEL DOM
    // =====================================================

    const establishmentName = document.getElementById("establishmentName");
    const adminName = document.getElementById("adminName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const totalClients = document.getElementById("totalClients");
    const clientsWithEmail = document.getElementById("clientsWithEmail");
    const clientsWithoutEmail = document.getElementById("clientsWithoutEmail");

    const searchClient = document.getElementById("searchClient");
    const clientsTableBody = document.getElementById("clientsTableBody");

    const emptyClients = document.getElementById("emptyClients");
    const emptyClientsTitle = document.getElementById("emptyClientsTitle");
    const emptyClientsDescription = document.getElementById("emptyClientsDescription");

    const loadingClients = document.getElementById("loadingClients");
    const clientsError = document.getElementById("clientsError");
    const clientsErrorMessage = document.getElementById("clientsErrorMessage");

    const retryClientsButton = document.getElementById("retryClientsButton");
    const refreshClientsButton = document.getElementById("refreshClientsButton");

    const clientModal = document.getElementById("clientModal");
    const clientForm = document.getElementById("clientForm");

    const clientId = document.getElementById("clientId");
    const clientName = document.getElementById("clientName");
    const clientPhone = document.getElementById("clientPhone");
    const clientEmail = document.getElementById("clientEmail");

    const modalTitle = document.getElementById("modalTitle");

    const addClientButton = document.getElementById("addClientButton");
    const saveClientButton = document.getElementById("saveClientButton");
    const cancelClientButton = document.getElementById("cancelClientButton");
    const closeClientModal = document.getElementById("closeClientModal");

    const clientFormMessage = document.getElementById("clientFormMessage");


    // =====================================================
    // ESTADO
    // =====================================================

    let clientes = [];
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
                throw new Error(
                    "La cuenta no corresponde a un establecimiento."
                );
            }

            const establecimiento = respuesta.data.establecimiento;

            if (!establecimiento) {
                throw new Error(
                    "No se encontraron los datos del establecimiento."
                );
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
    // MENSAJES DEL FORMULARIO
    // =====================================================

    function mostrarMensajeFormulario(mensaje, tipo = "error") {

        if (!clientFormMessage) return;

        clientFormMessage.textContent = mensaje;
        clientFormMessage.className = `form-message ${tipo}`;
        clientFormMessage.hidden = false;
    }

    function limpiarMensajeFormulario() {

        if (!clientFormMessage) return;

        clientFormMessage.textContent = "";
        clientFormMessage.hidden = true;
        clientFormMessage.className = "form-message";
    }


    // =====================================================
    // FORMATO DE TEXTO
    // =====================================================

    function obtenerNombre(nombre) {
        return nombre || "Sin nombre";
    }

    function obtenerCorreo(correo) {
        return correo ? correo : "No registrado";
    }


    // =====================================================
    // ACTUALIZAR ESTADÍSTICAS
    // =====================================================

    function actualizarEstadisticas() {

        const total = clientes.length;

        const conCorreo = clientes.filter(
            cliente => Boolean(cliente.correo)
        ).length;

        const sinCorreo = total - conCorreo;

        if (totalClients) {
            totalClients.textContent = total;
        }

        if (clientsWithEmail) {
            clientsWithEmail.textContent = conCorreo;
        }

        if (clientsWithoutEmail) {
            clientsWithoutEmail.textContent = sinCorreo;
        }
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
    // MOSTRAR CLIENTES
    // =====================================================

    function mostrarClientes(lista) {

        if (!clientsTableBody) return;

        clientsTableBody.replaceChildren();

        if (lista.length === 0) {

            if (emptyClients) {
                emptyClients.hidden = false;
            }

            if (clientes.length === 0) {

                if (emptyClientsTitle) {
                    emptyClientsTitle.textContent =
                        "No hay clientes registrados";
                }

                if (emptyClientsDescription) {
                    emptyClientsDescription.textContent =
                        "Agrega tu primer cliente para comenzar a administrar sus datos.";
                }

            } else {

                if (emptyClientsTitle) {
                    emptyClientsTitle.textContent =
                        "No se encontraron clientes";
                }

                if (emptyClientsDescription) {
                    emptyClientsDescription.textContent =
                        "Intenta buscar utilizando otro nombre o número de teléfono.";
                }
            }

            return;
        }

        if (emptyClients) {
            emptyClients.hidden = true;
        }

        lista.forEach(cliente => {

            const fila = document.createElement("tr");

            const nombre = obtenerNombre(cliente.nombre);
            const telefono = cliente.telefono || "No registrado";
            const correo = obtenerCorreo(cliente.correo);

            // NOMBRE
            const celdaNombre = crearCelda(nombre, "client-name");
            fila.appendChild(celdaNombre);

            // TELÉFONO
            fila.appendChild(
                crearCelda(telefono, "client-contact")
            );

            // CORREO
            const celdaCorreo = crearCelda(
                correo,
                cliente.correo ? "client-contact" : "no-email"
            );

            fila.appendChild(celdaCorreo);

            // ACCIONES
            const celdaAcciones = document.createElement("td");
            celdaAcciones.className = "actions-cell";

            const contenedorAcciones = document.createElement("div");
            contenedorAcciones.className = "actions-container";

            contenedorAcciones.appendChild(
                crearBoton(
                    "Editar",
                    "edit",
                    () => abrirModalEdicion(cliente),
                    "Editar cliente"
                )
            );

            contenedorAcciones.appendChild(
                crearBoton(
                    "Eliminar",
                    "delete",
                    () => eliminarCliente(cliente),
                    "Eliminar cliente"
                )
            );

            celdaAcciones.appendChild(contenedorAcciones);
            fila.appendChild(celdaAcciones);

            clientsTableBody.appendChild(fila);
        });
    }


    // =====================================================
    // BUSCAR CLIENTES
    // =====================================================

    function aplicarBusqueda() {

        const busqueda = searchClient
            ? searchClient.value.trim().toLowerCase()
            : "";

        const resultado = clientes.filter(cliente => {

            const nombre = (cliente.nombre || "").toLowerCase();
            const telefono = (cliente.telefono || "").toLowerCase();
            const correo = (cliente.correo || "").toLowerCase();

            return (
                nombre.includes(busqueda) ||
                telefono.includes(busqueda) ||
                correo.includes(busqueda)
            );
        });

        mostrarClientes(resultado);
    }

    if (searchClient) {
        searchClient.addEventListener("input", aplicarBusqueda);
    }


    // =====================================================
    // CONSULTAR CLIENTES
    // =====================================================

    async function cargarClientes() {

        if (cargando) return;

        cargando = true;

        if (loadingClients) {
            loadingClients.hidden = false;
        }

        if (clientsError) {
            clientsError.hidden = true;
        }

        if (emptyClients) {
            emptyClients.hidden = true;
        }

        if (refreshClientsButton) {
            refreshClientsButton.disabled = true;
        }

        try {

            const respuesta = await window.API.get("/clients/");

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje ||
                    "No fue posible consultar los clientes."
                );
            }

            if (!Array.isArray(respuesta.data)) {
                throw new Error(
                    "El servidor devolvió una lista de clientes inválida."
                );
            }

            clientes = respuesta.data;

            actualizarEstadisticas();
            aplicarBusqueda();

        } catch (error) {

            console.error("Error al consultar clientes:", error);

            if (clientsErrorMessage) {
                clientsErrorMessage.textContent = error.message;
            }

            if (clientsError) {
                clientsError.hidden = false;
            }

        } finally {

            cargando = false;

            if (loadingClients) {
                loadingClients.hidden = true;
            }

            if (refreshClientsButton) {
                refreshClientsButton.disabled = false;
            }
        }
    }


    // =====================================================
    // ABRIR Y CERRAR MODAL
    // =====================================================

    function abrirModal() {

        if (!clientModal) return;

        limpiarMensajeFormulario();

        clientModal.hidden = false;
        clientModal.setAttribute("aria-hidden", "false");

        if (clientName) {
            clientName.focus();
        }
    }

    function cerrarModal() {

        if (!clientModal) return;

        clientModal.hidden = true;
        clientModal.setAttribute("aria-hidden", "true");

        if (clientForm) {
            clientForm.reset();
        }

        if (clientId) {
            clientId.value = "";
        }

        limpiarMensajeFormulario();
    }


    // =====================================================
    // REGISTRAR CLIENTE
    // =====================================================

    function abrirModalRegistro() {

        if (!clientForm) return;

        clientForm.reset();

        if (clientId) {
            clientId.value = "";
        }

        if (modalTitle) {
            modalTitle.textContent = "Agregar cliente";
        }

        if (saveClientButton) {
            saveClientButton.textContent = "Guardar cliente";
        }

        abrirModal();
    }


    // =====================================================
    // EDITAR CLIENTE
    // =====================================================

    function abrirModalEdicion(cliente) {

        if (!clientForm) return;

        clientForm.reset();

        if (clientId) {
            clientId.value = cliente.id_cliente;
        }

        if (clientName) {
            clientName.value = cliente.nombre || "";
        }

        if (clientPhone) {
            clientPhone.value = cliente.telefono || "";
        }

        if (clientEmail) {
            clientEmail.value = cliente.correo || "";
        }

        if (modalTitle) {
            modalTitle.textContent = "Editar cliente";
        }

        if (saveClientButton) {
            saveClientButton.textContent = "Guardar cambios";
        }

        abrirModal();
    }


    // =====================================================
    // VALIDAR FORMULARIO
    // =====================================================

    function obtenerDatosFormulario() {

        const nombre = clientName.value.trim();
        const telefono = clientPhone.value.trim();
        const correo = clientEmail.value.trim();

        if (!nombre) {
            throw new Error("El nombre del cliente es obligatorio.");
        }

        if (nombre.length > 100) {
            throw new Error(
                "El nombre no puede superar los 100 caracteres."
            );
        }

        if (!telefono) {
            throw new Error("El teléfono del cliente es obligatorio.");
        }

        if (telefono.length > 20) {
            throw new Error(
                "El teléfono no puede superar los 20 caracteres."
            );
        }

        if (!/^[0-9+\-() ]+$/.test(telefono)) {
            throw new Error(
                "El teléfono contiene caracteres no permitidos."
            );
        }

        if (correo.length > 100) {
            throw new Error(
                "El correo no puede superar los 100 caracteres."
            );
        }

        if (correo) {

            const expresionCorreo =
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!expresionCorreo.test(correo)) {
                throw new Error(
                    "Ingresa un correo electrónico válido."
                );
            }
        }

        return {
            nombre,
            telefono,
            correo: correo || null
        };
    }


    // =====================================================
    // GUARDAR CLIENTE
    // =====================================================

    async function guardarCliente(evento) {

        evento.preventDefault();

        limpiarMensajeFormulario();

        let datos;

        try {

            datos = obtenerDatosFormulario();

        } catch (error) {

            mostrarMensajeFormulario(error.message);
            return;
        }

        const id = clientId ? clientId.value : "";
        const esEdicion = Boolean(id);

        try {

            if (saveClientButton) {
                saveClientButton.disabled = true;
                saveClientButton.textContent = "Guardando...";
            }

            let respuesta;

            if (esEdicion) {

                respuesta = await window.API.put(
                    `/clients/${id}`,
                    datos
                );

            } else {

                respuesta = await window.API.post(
                    "/clients/",
                    datos
                );
            }

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje ||
                    "No fue posible guardar el cliente."
                );
            }

            alert(
                respuesta.mensaje ||
                (
                    esEdicion
                        ? "Cliente actualizado correctamente."
                        : "Cliente registrado correctamente."
                )
            );

            cerrarModal();

            await cargarClientes();

        } catch (error) {

            console.error("Error al guardar cliente:", error);

            mostrarMensajeFormulario(error.message);

        } finally {

            if (saveClientButton) {
                saveClientButton.disabled = false;

                saveClientButton.textContent = esEdicion
                    ? "Guardar cambios"
                    : "Guardar cliente";
            }
        }
    }


    // =====================================================
    // ELIMINAR CLIENTE
    // =====================================================

    async function eliminarCliente(cliente) {

        const confirmar = window.confirm(
            `¿Estás seguro de que deseas eliminar al cliente "${cliente.nombre}"?`
        );

        if (!confirmar) return;

        try {

            const respuesta = await window.API.delete(
                `/clients/${cliente.id_cliente}`
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje ||
                    "No fue posible eliminar el cliente."
                );
            }

            alert(
                respuesta.mensaje ||
                "Cliente eliminado correctamente."
            );

            await cargarClientes();

        } catch (error) {

            console.error("Error al eliminar cliente:", error);

            alert(error.message);
        }
    }


    // =====================================================
    // EVENTOS DEL MODAL
    // =====================================================

    if (addClientButton) {
        addClientButton.addEventListener(
            "click",
            abrirModalRegistro
        );
    }

    if (closeClientModal) {
        closeClientModal.addEventListener(
            "click",
            cerrarModal
        );
    }

    if (cancelClientButton) {
        cancelClientButton.addEventListener(
            "click",
            cerrarModal
        );
    }

    if (clientForm) {
        clientForm.addEventListener(
            "submit",
            guardarCliente
        );
    }

    if (clientModal) {

        clientModal.addEventListener("click", evento => {

            if (evento.target === clientModal) {
                cerrarModal();
            }
        });
    }

    document.addEventListener("keydown", evento => {

        if (
            evento.key === "Escape" &&
            clientModal &&
            !clientModal.hidden
        ) {
            cerrarModal();
        }
    });


    // =====================================================
    // ACTUALIZAR Y REINTENTAR
    // =====================================================

    if (retryClientsButton) {
        retryClientsButton.addEventListener(
            "click",
            cargarClientes
        );
    }

    if (refreshClientsButton) {
        refreshClientsButton.addEventListener(
            "click",
            cargarClientes
        );
    }


    // =====================================================
    // INICIALIZACIÓN
    // =====================================================

    const sesionValida = await validarSesion();

    if (sesionValida) {
        await cargarClientes();
    }

});
