import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_cors_origins, get_secret_key
from .database import init_db
from . import models
from .routers import auth, proposals

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("freelatracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FreelaTracker API", lifespan=lifespan)

allowed_origins = get_cors_origins()
# Validar que el secreto este definido al iniciar
get_secret_key()


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Archivos estáticos (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates HTML
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Routers de la API
app.include_router(auth.router)
app.include_router(proposals.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error processing %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado. Intenta más tarde."},
    )
