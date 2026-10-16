from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC_PATHS = (
    "/login",
    "/logout",
    "/static",
    "/favicon.ico",
    "/captcha-refresh",
    "/cambiar-clave",
    "/reclamoVecino"
)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # rutas públicas
        if path.startswith(PUBLIC_PATHS):
            return await call_next(request)

        if request.url.path.startswith("/captcha"):
            return await call_next(request)

        # requiere sesión
        if not request.session.get("user") or not request.session.get("user_id"):
            request.session.clear()
            return RedirectResponse("/login", status_code=302)

        

        return await call_next(request)
