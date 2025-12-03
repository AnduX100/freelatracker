# FreelaTracker · AnduX Dev

Panel personal para llevar el control de mis propuestas de **Workana / Freelancer** en un solo lugar.  
Permite registrar, filtrar y revisar el estado de cada oportunidad, con estadísticas básicas de cierre.

> Proyecto de uso personal desarrollado por **AnduX Dev** (Medellín, Colombia) con **Python + FastAPI + PostgreSQL (Neon)**.

---

## 🚀 Funcionalidades

- ✉️ **Autenticación de usuario propia** (no usa tu contraseña real de Workana/Freelancer).
- 📥 **Registro de propuestas** con:
  - Cliente
  - Plataforma (Workana, Freelancer, etc.)
  - Título del proyecto
  - Link a la publicación
  - Monto ofertado + moneda
  - Estado (Enviada, En negociación, Aceptada, Rechazada, Borrador)
  - Notas internas
- 📋 **Tabla de propuestas** filtrada por usuario autenticado.
- 📊 **Estadísticas básicas**:
  - Total de propuestas
  - Aceptadas
  - Rechazadas
  - Pendientes
  - Tasa de cierre (%)
- 🧹 UI oscura, compacta y pensada para uso diario mientras se aplican proyectos.

---

## 🧱 Stack tecnológico

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend:** HTML + CSS puro (estilo dashboard dark)
- **Base de datos dev:** SQLite (archivo local)
- **Base de datos prod:** PostgreSQL en [Neon](https://neon.tech/) (plan gratuito)
- **ORM:** SQLAlchemy
- **Auth:** JWT (tokens de acceso + lista de tokens revocados)
- **Servidor ASGI:** Uvicorn

Tablas principales:

- `users`
- `proposals`
- `revoked_tokens`

---

## 🖼️ Screenshots



- **Pantalla principal (login + propuestas)**  
  ![FreelaTracker dashboard](docs/screenshots/dashboard.png)

---

## 📂 Estructura básica del proyecto

```bash
freelatracker/
├── app/
│   ├── main.py           # Punto de entrada FastAPI
│   ├── config.py         # Configuración y lectura de env vars
│   ├── database.py       # Motor SQLAlchemy y sesión
│   ├── models.py         # Modelos ORM (User, Proposal, RevokedToken)
│   ├── schemas.py        # Esquemas Pydantic
│   ├── auth.py           # Lógica de autenticación y JWT
│   ├── routers/
│   │   ├── auth.py       # /auth/login, /auth/register, etc.
│   │   └── proposals.py  # CRUD de propuestas + stats
│   └── static/
│       ├── index.html    # UI principal
│       └── styles.css    # Estilos del dashboard
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

```

## 🧪 Ejecutar en local (modo dev)

1. Clonar el repo
```bash
git clone https://github.com/AnduX100/freelatracker.git
cd freelatracker
```
2. Crear entorno virtual
```bash
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
```
3. Instalar dependencias
```bash
pip install -r requirements.txt
```
4. Configurar .env para desarrollo
```bash
cp .env.example .env
```
Esto levanta SQLite en un archivo local freelatracker.db.

5. Levantar el servidor
```bash
uvicorn app.main:app --reload
```
Abrir en el navegador:
- http://127.0.0.1:8000

## 🗄️ Uso con PostgreSQL (Neon) en prod/staging

1. Crea un proyecto gratuito en Neon.
2. Obtén la cadena de conexión en formato psycopg2.
3. Exporta las variables de entorno, por ejemplo en PowerShell:
```bash
$env:FREELATRACKER_ENV = "prod"
$env:FREELATRACKER_SECRET_KEY = "<tu_clave_super_larga_y_secreta>"
$env:FREELATRACKER_DATABASE_URL = "postgresql+psycopg2://USER:PASS@HOST/dbname"
$env:FREELATRACKER_AUTO_CREATE_TABLES = "false"
```
4. Aplica el SQL de creación de tablas en Neon (users, proposals, revoked_tokens).
5. Arranca el servidor:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Si apagas y vuelves a prender el server y tus propuestas siguen ahí, estás leyendo datos desde Neon correctamente.

## 🛡️ Notas de seguridad

- No guardes tus contraseñas reales de Workana / Freelancer aquí.
- En producción se recomienda usar HTTPS y un proxy (Nginx, etc.) frente a la app.

## 🗺️ Roadmap

- Filtros por rango de fechas y plataforma.
- Exportar propuestas a CSV/Excel.
- Tags por tipo de proyecto (Python, AWS, IA, etc.).
- Dashboard de gráficos.
- Multi-idioma (ES/EN).
