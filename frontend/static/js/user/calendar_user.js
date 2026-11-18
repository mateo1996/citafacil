
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS DEL DOM
    // =====================================

    const userName = document.getElementById("userName");
    const userAvatar = document.getElementById("userAvatar");
    const logoutButton = document.getElementById("logoutButton");

    const establishmentSelect = document.getElementById(
        "establishmentSelect"
    );

    const serviceSelect = document.getElementById(
        "serviceSelect"
    );

    const appointmentDate = document.getElementById(
        "appointmentDate"
    );

    const availableSlots = document.getElementById(
        "availableSlots"
    );

    const bookingForm = document.getElementById("bookingForm");
    const bookingMessage = document.getElementById("bookingMessage");
    const submitBooking = document.getElementById("submitBooking");


    // =====================================
    // ESTADO
    // =====================================

    let establecimientoSeleccionado = null;
    let servicioSeleccionado = null;
    let serviciosEstablecimiento = [];
    let horariosEstablecimiento = [];
    let horaSeleccionada = null;


    // =====================================
    // UTILIDADES
    // =====================================

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


    function mostrarMensaje(mensaje, tipo = "info") {
        bookingMessage.textContent = mensaje;
        bookingMessage.className = `booking-message ${tipo}`;
    }


    function limpiarMensaje() {
        bookingMessage.textContent = "";
        bookingMessage.className = "booking-message";
    }


    function obtenerDatos(respuesta) {
        if (!respuesta || respuesta.ok !== true) {
            throw new Error(
                respuesta?.mensaje || "No fue posible obtener la información."
            );
        }

        return respuesta.data;
    }


    function obtenerDiaSemana(fecha) {
        const dias = [
            "domingo",
            "lunes",
            "martes",
            "miercoles",
            "jueves",
            "viernes",
            "sabado"
        ];

        return dias[new Date(`${fecha}T12:00:00`).getDay()];
    }

    function convertirHoraAMinutos(hora) {
        const [horas, minutos] = hora.split(":").map(Number);

        return horas * 60 + minutos;
    }


    function convertirMinutosAHora(minutos) {
        const horas = Math.floor(minutos / 60);
        const minutosRestantes = minutos % 60;

        return `${String(horas).padStart(2, "0")}:${String(minutosRestantes).padStart(2, "0")}`;
    }


    // =====================================
    // VALIDAR SESIÓN
    // =====================================

    async function validarSesion() {
        try {
            const respuesta = await API.get("/auth/validate");

            if (!respuesta.ok) {
                window.location.href = "/";
                return false;
            }

            const usuario = respuesta.data?.usuario;

            if (
                !usuario ||
                respuesta.data?.tipo_cuenta !== "cliente"
            ) {
                window.location.href = "/";
                return false;
            }

            const nombre = usuario.nombre || "Usuario";

            userName.textContent = nombre;
            userAvatar.textContent = nombre.trim()
                .charAt(0)
                .toUpperCase();

            return true;

        } catch (error) {
            console.error("Error al validar la sesión:", error);
            window.location.href = "/";
            return false;
        }
    }


    // =====================================
    // CARGAR ESTABLECIMIENTOS
    // =====================================

    async function cargarEstablecimientos() {
        try {
            establishmentSelect.disabled = true;

            const respuesta = await API.get(
                "/establishments/available"
            );

            const establecimientos = obtenerDatos(respuesta);

            if (!Array.isArray(establecimientos)) {
                throw new Error(
                    "El servidor devolvió una lista de establecimientos inválida."
                );
            }

            establishmentSelect.innerHTML = `
                <option value="">
                    Selecciona un establecimiento
                </option>
            `;

            establecimientos.forEach(establecimiento => {

                const opcion = document.createElement("option");

                opcion.value = establecimiento.id_establecimiento;

                opcion.textContent =
                    establecimiento.nombre_comercial;

                establishmentSelect.appendChild(opcion);

            });

            if (establecimientos.length === 0) {
                mostrarMensaje(
                    "Actualmente no hay establecimientos disponibles.",
                    "info"
                );
            }

        } catch (error) {
            console.error("Error al cargar establecimientos:", error);

            mostrarMensaje(
                error.message || "No fue posible cargar los establecimientos.",
                "error"
            );

        } finally {
            establishmentSelect.disabled = false;
        }
    }


    // =====================================
    // CARGAR SERVICIOS
    // =====================================

    async function cargarServicios(idEstablecimiento) {

        try {

            serviceSelect.disabled = true;

            serviceSelect.innerHTML = `
                <option value="">
                    Cargando servicios...
                </option>
            `;

            const respuesta = await API.get(
                `/services/available/${idEstablecimiento}`
            );

            const servicios = obtenerDatos(respuesta);

            serviciosEstablecimiento = servicios;

            if (!Array.isArray(servicios)) {
                throw new Error("La lista de servicios no es válida.");
            }
            serviciosEstablecimiento = servicios;
            serviceSelect.innerHTML = `
                <option value="">
                    Selecciona un servicio
                </option>
            `;

            servicios.forEach(servicio => {

                const opcion = document.createElement("option");

                opcion.value = servicio.id_servicio;

                opcion.textContent =
                    `${servicio.nombre} - ${Number(servicio.precio).toLocaleString("es-CO")} COP (${servicio.duracion_minutos} min)`;

                serviceSelect.appendChild(opcion);

            });

            if (servicios.length === 0) {

                serviceSelect.innerHTML = `
                    <option value="">
                        No hay servicios disponibles
                    </option>
                `;

                mostrarMensaje(
                    "Este establecimiento no tiene servicios disponibles.",
                    "info"
                );

                return;
            }

            serviceSelect.disabled = false;

        } catch (error) {

            console.error("Error al cargar servicios:", error);

            serviceSelect.innerHTML = `
                <option value="">
                    Error al cargar servicios
                </option>
            `;

            mostrarMensaje(
                error.message || "No fue posible cargar los servicios.",
                "error"
            );

        }

    }


    // =====================================
    // CARGAR HORARIOS DEL ESTABLECIMIENTO
    // =====================================

    async function cargarHorarios(idEstablecimiento) {

        try {

            const respuesta = await API.get(
                `/schedules/available/${idEstablecimiento}`
            );

            const horarios = obtenerDatos(respuesta);

            if (!Array.isArray(horarios)) {
                throw new Error("La lista de horarios no es válida.");
            }

            horariosEstablecimiento = horarios;

            return horarios;

        } catch (error) {

            console.error("Error al cargar horarios:", error);

            horariosEstablecimiento = [];

            mostrarMensaje(
                error.message || "No fue posible cargar los horarios.",
                "error"
            );

            return [];

        }
    }


    // =====================================
    // GENERAR HORARIOS PARA LA FECHA
    // =====================================

    function generarHorarios(fecha) {

        availableSlots.innerHTML = "";
        horaSeleccionada = null;
        submitBooking.disabled = true;

        const diaSeleccionado = obtenerDiaSemana(fecha);

        const horario = horariosEstablecimiento.find(
            item => item.dia === diaSeleccionado
        );

        if (!horario) {
            availableSlots.innerHTML = `
                <p class="slots-placeholder">
                    El establecimiento no atiende este día.
                </p>
            `;
            return;
        }

        const duracion = Number(
            servicioSeleccionado?.duracion_minutos
        );

        if (!Number.isFinite(duracion) || duracion <= 0) {
            mostrarMensaje(
                "La duración del servicio no es válida.",
                "error"
            );
            return;
        }

        const inicioJornada = convertirHoraAMinutos(
            horario.hora_inicio
        );

        const finJornada = convertirHoraAMinutos(
            horario.hora_fin
        );

        const inicioDescanso = horario.hora_inicio_descanso
            ? convertirHoraAMinutos(horario.hora_inicio_descanso)
            : null;

        const finDescanso = horario.hora_fin_descanso
            ? convertirHoraAMinutos(horario.hora_fin_descanso)
            : null;

        const intervalo = 15;

        const hoy = new Date();

        const fechaHoy = [
            hoy.getFullYear(),
            String(hoy.getMonth() + 1).padStart(2, "0"),
            String(hoy.getDate()).padStart(2, "0")
        ].join("-");

        const minutosActuales =
            hoy.getHours() * 60 + hoy.getMinutes();

        let cantidadHorarios = 0;

        for (
            let inicio = inicioJornada;
            inicio + duracion <= finJornada;
            inicio += intervalo
        ) {

            const fin = inicio + duracion;

            // Evitar horarios anteriores a la hora actual.
            if (fecha === fechaHoy && inicio <= minutosActuales) {
                continue;
            }

            // Evitar horarios que coincidan con el descanso.
            if (
                inicioDescanso !== null &&
                finDescanso !== null &&
                inicio < finDescanso &&
                fin > inicioDescanso
            ) {
                continue;
            }

            const hora = convertirMinutosAHora(inicio);

            const boton = document.createElement("button");

            boton.type = "button";
            boton.className = "slot-button";
            boton.textContent = hora;

            boton.addEventListener("click", () => {

                horaSeleccionada = hora;

                availableSlots
                    .querySelectorAll(".slot-button")
                    .forEach(elemento => {
                        elemento.classList.remove("selected");
                    });

                boton.classList.add("selected");

                submitBooking.disabled = false;

                limpiarMensaje();

            });

            availableSlots.appendChild(boton);

            cantidadHorarios++;

        }

        if (cantidadHorarios === 0) {
            availableSlots.innerHTML = `
                <p class="slots-placeholder">
                    No hay horarios de atención disponibles
                    para esta fecha y servicio.
                </p>
            `;
        }

    }


    // =====================================
    // SELECCIONAR SERVICIO
    // =====================================

    serviceSelect.addEventListener("change", () => {

        servicioSeleccionado = serviciosEstablecimiento.find(
            servicio =>
                String(servicio.id_servicio) === serviceSelect.value
        ) || null;

        horaSeleccionada = null;

        appointmentDate.value = "";
        appointmentDate.disabled = !servicioSeleccionado;

        if (servicioSeleccionado) {
            const hoy = new Date();
            const fechaLocal = [
                hoy.getFullYear(),
                String(hoy.getMonth() + 1).padStart(2, "0"),
                String(hoy.getDate()).padStart(2, "0")
            ].join("-");

            appointmentDate.min = fechaLocal;
        }

        availableSlots.innerHTML = `
            <p class="slots-placeholder">
                Selecciona una fecha para consultar los horarios.
            </p>
        `;

        submitBooking.disabled = true;

        limpiarMensaje();

    });


    // =====================================
    // SELECCIONAR FECHA
    // =====================================

    appointmentDate.addEventListener("change", () => {

        horaSeleccionada = null;
        submitBooking.disabled = true;

        limpiarMensaje();

        if (!appointmentDate.value || !servicioSeleccionado) {
            availableSlots.innerHTML = `
                <p class="slots-placeholder">
                    Selecciona un servicio y una fecha.
                </p>
            `;
            return;
        }

        generarHorarios(appointmentDate.value);

    });


    // =====================================
    // SELECCIONAR ESTABLECIMIENTO
    // =====================================

    establishmentSelect.addEventListener("change", async () => {

        establecimientoSeleccionado = establishmentSelect.value;

        servicioSeleccionado = null;
        horariosEstablecimiento = [];
        horaSeleccionada = null;

        serviceSelect.innerHTML = `
            <option value="">
                Selecciona un servicio
            </option>
        `;

        serviceSelect.disabled = true;
        appointmentDate.value = "";
        appointmentDate.disabled = true;

        availableSlots.innerHTML = `
            <p class="slots-placeholder">
                Selecciona un servicio y una fecha.
            </p>
        `;

        submitBooking.disabled = true;
        limpiarMensaje();

        if (!establecimientoSeleccionado) {
            serviceSelect.innerHTML = `
                <option value="">
                    Primero selecciona un establecimiento
                </option>
            `;

            return;
        }

        await Promise.all([
            cargarServicios(establecimientoSeleccionado),
            cargarHorarios(establecimientoSeleccionado)
        ]);

    });


    // =====================================
    // REGISTRAR RESERVA DEL CLIENTE
    // =====================================

    bookingForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        if (
            !establecimientoSeleccionado ||
            !servicioSeleccionado ||
            !appointmentDate.value ||
            !horaSeleccionada
        ) {
            mostrarMensaje(
                "Completa todos los datos y selecciona un horario.",
                "error"
            );
            return;
        }

        const datosReserva = {
            id_establecimiento: Number(establecimientoSeleccionado),
            id_servicio: Number(servicioSeleccionado.id_servicio),
            fecha: appointmentDate.value,
            hora_inicio: horaSeleccionada
        };

        submitBooking.disabled = true;
        submitBooking.textContent = "Reservando...";

        limpiarMensaje();

        try {

            const respuesta = await API.post(
                "/users/appointments",
                datosReserva
            );

            if (!respuesta.ok) {
                throw new Error(
                    respuesta.mensaje || "No fue posible reservar la cita."
                );
            }

            mostrarMensaje(
                respuesta.mensaje || "¡Tu cita fue reservada correctamente!",
                "success"
            );

            window.location.href = "/user";

        } catch (error) {

            mostrarMensaje(
                error.message || "Ocurrió un error al reservar la cita.",
                "error"
            );

            submitBooking.disabled = false;
            submitBooking.textContent = "Reservar cita";

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

    async function inicializarCalendario() {

        const sesionValida = await validarSesion();

        if (!sesionValida) {
            return;
        }

        await cargarEstablecimientos();

    }

    inicializarCalendario();

});
