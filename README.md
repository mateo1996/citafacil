# CitaFácil

Sistema web de gestión de citas que permite conectar establecimientos y usuarios para administrar servicios, horarios y reservas.

## Arquitectura

El proyecto está organizado en tres componentes:

- **Backend:** API desarrollada con Python y Flask. Gestiona usuarios, autenticación, establecimientos, servicios, horarios y citas.
- **Frontend:** interfaz web desarrollada con HTML, CSS, JavaScript y Flask.
- **Proxy:** intermediario que conecta el frontend con el backend.

### Puertos locales

| Componente | Dirección |
|---|---|
| Backend | http://127.0.0.1:5000 |
| Frontend | http://127.0.0.1:5001 |
| Proxy | http://127.0.0.1:5002 |

La aplicación se utiliza desde:

http://127.0.0.1:5002

## Tecnologías utilizadas

- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- JWT
- bcrypt
- WhatsApp Cloud API
- SMTP para envío de correos

## Estructura del proyecto

```text
sistema_gestion_citas/
│
├── backend/
│   ├── apps/
│   ├── config/
│   ├── infrastructure/
│   ├── .env.example
│   ├── requirements.txt
│   └── app.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── app.py
│
├── database/
│
├── proxy.py
├── .env.example
├── .gitignore
└── README.md
```

## Requisitos

- Python instalado.
- MySQL instalado y configurado.
- Git.
- Un navegador web.

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd sistema_gestion_citas
```

### 2. Crear un entorno virtual

Desde la raíz del proyecto:

```bash
py -m venv .venv
```

Activarlo en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
py -m pip install -r backend/requirements.txt
```

### 4. Configurar las variables de entorno

Crear el archivo de configuración local:

```powershell
Copy-Item .\backend\.env.example .\backend\.env
```

Editar `backend/.env` y completar los valores correspondientes a:

- Claves de seguridad y JWT.
- Conexión a la base de datos MySQL.
- Configuración del servidor de correo.
- Credenciales de integración con WhatsApp Cloud API.
- Configuración general del entorno.

**Importante:** no compartir ni subir el archivo `backend/.env` al repositorio. Contiene información privada.

### 5. Configurar MySQL

Crear y configurar la base de datos MySQL correspondiente al proyecto.

Los datos de conexión deben coincidir con los valores definidos en `backend/.env`.

El repositorio no incluye un script SQL de creación de la base de datos; se debe disponer previamente del esquema requerido por la aplicación.

## Ejecución del proyecto

Se deben abrir tres terminales de PowerShell, ubicadas en la raíz del proyecto, y mantener los procesos activos.

### Terminal 1: Backend

```powershell
cd backend
py app.py
```

El backend se ejecutará en:

http://127.0.0.1:5000

### Terminal 2: Frontend

```powershell
cd frontend
py app.py
```

El frontend se ejecutará en:

http://127.0.0.1:5001

### Terminal 3: Proxy

Desde la raíz del proyecto:

```powershell
py proxy.py
```

El proxy se ejecutará en:

http://127.0.0.1:5002

### Acceder al sistema

Abrir en el navegador:

http://127.0.0.1:5002

## Integraciones externas

El proyecto contempla integraciones para:

- Envío de correos electrónicos mediante SMTP.
- Notificaciones de WhatsApp mediante WhatsApp Cloud API.

Estas integraciones requieren sus respectivas credenciales y variables de entorno configuradas localmente.

## Seguridad

- Los archivos `.env` no deben publicarse.
- No incluir contraseñas, tokens ni credenciales en el código fuente.
- Mantener las claves privadas fuera del repositorio.
- Configurar adecuadamente las variables de entorno antes de ejecutar la aplicación.

## Autoría

Proyecto de grado: **CitaFácil**.
