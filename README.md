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
