import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config.auth import AuthMiddleware
from config.security import limiter
from config.settings import settings

from routers.categoria_router import router as categoria_router
from routers.inspector_router import router as inspector_router
from routers.localidad_router import router as localidad_router
from routers.publico_router import router as publico_router
from routers.reclamo_router import router as reclamo_router
from routers.usuario_router import router as usuario_router

# ----------------------
# IMPORTAR MODELOS (REGISTRA RELACIONES)
# ----------------------
import models

# ----------------------
# LOGGING
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# ----------------------
# INSTANCIA ÚNICA DE FASTAPI
# ----------------------
app = FastAPI(
    title="Dirección de Bromatología - Municipalidad de 9 de Julio", debug=True
)

# ----------------------
# RATE LIMITER (Intentos)
# ----------------------
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
  return JSONResponse(
      status_code=429,
      content={"detail": "Demasiados intentos. Intente más tarde."},
  )


# ----------------------
# AUTH MIDDLEWARE
# ----------------------
app.add_middleware(AuthMiddleware)

# ----------------------
# SESSION
# ----------------------
SESSION_SECRET_KEY = settings.SECRET_KEY
if not SESSION_SECRET_KEY:
  raise RuntimeError("No se encontró la variable SECRET_KEY")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SESSION_SECRET_KEY,
    same_site="lax" #,      # Fundamental para navegadores modernos O  same_site="strict"
    #https_only=true      # False si estás probando en http://127.0.0.1 o localhost
)

# ----------------------
# STATIC
# ----------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------
# uploads - Carga de evidencia de los reclamos
# ----------------------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ----------------------
# ROOT
# ----------------------
@app.get("/")
def root():
  return RedirectResponse("/login")

templates = Jinja2Templates(directory="templates")

# ----------------------
# ROUTERS
# ----------------------
# Pasamos las variables directamente (ya son APIRouter)
app.include_router(publico_router)
app.include_router(usuario_router, prefix="", tags=["usuario"])
app.include_router(inspector_router, prefix="", tags=["inspectores"])
app.include_router(localidad_router, prefix="", tags=["localidad"])
app.include_router(categoria_router, prefix="", tags=["categoria"])
app.include_router(reclamo_router, prefix="", tags=["reclamo"])

