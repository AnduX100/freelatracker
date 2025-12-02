# FreelaTracker

Pequena API + frontend estatico para registrar propuestas freelance con FastAPI.

## Requisitos
- Python 3.10+
- `pip` y `venv`

## Configuracion rapida (dev)
1. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia las variables de ejemplo y ajustalas:
   ```bash
   cp .env.example .env
   # define FREELATRACKER_SECRET_KEY con 32+ caracteres aleatorios (solo dev)
   ```
   El archivo `.env` se carga automaticamente solo si `FREELATRACKER_ENV` es `dev|local` (o si fuerzas `FREELATRACKER_LOAD_ENV_FILE=true`). En produccion evita `.env` y exporta las variables directamente.
4. Ejecuta el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Abre `http://localhost:8000` en el navegador.

## Variables de entorno claves
- `FREELATRACKER_SECRET_KEY` (obligatoria): clave larga para firmar JWT.
- `FREELATRACKER_DATABASE_URL`: URL SQLAlchemy (por defecto SQLite local).
- `FREELATRACKER_CORS_ORIGINS`: lista separada por comas de origenes permitidos.
- `FREELATRACKER_ACCESS_TOKEN_MINUTES`: minutos de vigencia del token.
- `FREELATRACKER_AUTO_CREATE_TABLES`: `true/false` para crear tablas en arranque. Por defecto `true` en dev y `false` si `FREELATRACKER_ENV=prod`.
- `FREELATRACKER_ENV`: `dev|local|prod|staging` controla carga de `.env` y auto-creacion de tablas.
- `FREELATRACKER_LOAD_ENV_FILE`: fuerza la carga (o no) de `.env` en dev.

## Migraciones
Usa Alembic para versionar el esquema. La creacion automatica de tablas es solo para desarrollo local; en produccion configura Alembic y desactiva `FREELATRACKER_AUTO_CREATE_TABLES` o define `FREELATRACKER_ENV=prod`.

## Pruebas
```bash
pytest
```

## Seguridad y operacion
- Rate limiting en `/auth/login` (ventana 5 min, 10 intentos) protegido con lock para entornos multi-hilo.
- JWT incluye `jti` y revocacion en `/auth/logout`; los tokens cerrados se bloquean para el resto de su vigencia.
- Claves y secretos solo via variables de entorno; no se versiona `.env` en prod.
- Auto-creacion de tablas desactivada por defecto en `prod`; usa migraciones.
- Politica de contrasena: requiere letras, numeros y caracter especial.
- CORS configurable via `FREELATRACKER_CORS_ORIGINS`.

# Activar venv
.\venv\Scripts\activate

# Variables (cuando uses Neon)
$env:FREELATRACKER_ENV = "prod"
$env:FREELATRACKER_DATABASE_URL = "postgresql+psycopg2://..."
$env:FREELATRACKER_SECRET_KEY = "...."
$env:FREELATRACKER_AUTO_CREATE_TABLES = "false"

# Levantar server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

