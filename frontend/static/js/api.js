
//const API_BASE_URL = "http://127.0.0.1:5000/api";

const API_BASE_URL = "/api";

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("El servidor devolvió una respuesta inválida.");
    }

    if (!response.ok) {
        throw new Error(
            data.mensaje || "Error al comunicarse con el servidor."
        );
    }

    return data;
}

const API = {
    get(endpoint) {
        return apiRequest(endpoint, {
            method: "GET"
        });
    },

    post(endpoint, datos) {
        return apiRequest(endpoint, {
            method: "POST",
            body: JSON.stringify(datos)
        });
    },

    put(endpoint, datos) {
        return apiRequest(endpoint, {
            method: "PUT",
            body: JSON.stringify(datos)
        });
    },

    patch(endpoint, datos) {
        return apiRequest(endpoint, {
            method: "PATCH",
            body: JSON.stringify(datos)
        });
    },

    delete(endpoint) {
        return apiRequest(endpoint, {
            method: "DELETE"
        });
    }
};

window.API = API;
