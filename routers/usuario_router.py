from fastapi import APIRouter, Depends, Body, Form, Request,Response
from sqlmodel import Session

from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import status

from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import random
import string
import io
import math

from models.usuario_model import UsuarioModel
from services.usuario_service import UsuarioService

from config.conexion import get_session

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@router.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@router.get("/indexPpal")
async def indexPpal(request: Request):
    return templates.TemplateResponse(
        "indexPpal.html",
        {
            "request": request,
            "hide_layout": False
        }
    )

@router.post("/login")
async def login(
    request: Request,
    usuario: str = Form(...),
    clave: str = Form(...),
    captcha: str = Form(...),
    website: str = Form(None),
    session: Session = Depends(get_session)
):

    # ----------------------
    # 1. HONEYPOT CHECK
    # ----------------------
    if website:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "Acceso inválido"
        })

    # ----------------------
    # 2. CAPTCHA CHECK
    # ----------------------
    captcha_session = request.session.get("captcha")
    
    if not captcha_session:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "Captcha expirado o no generado",
            "usuario": usuario
        })

    if captcha.lower().strip() != captcha_session.lower().strip():
        # NO generes captcha aquí; el navegador al recargar la plantilla 
        # o refrescar la imagen llamará a GET /captcha y actualizará la sesión.
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "Captcha incorrecto",
            "usuario": usuario
        })
    
        
    # ----------------------
    # 3. LIMPIAR CAPTCHA 
    # Invalidar captcha (anti replay)
    # ----------------------
    request.session.pop("captcha", None)

    # ----------------------
    # 4. AUTENTICACIÓN
    # ----------------------
    service = UsuarioService(session)

    auth_result = service.authenticate(usuario, clave)

    if auth_result is None:
        new_captcha = generar_captcha()
        request.session["captcha"] = new_captcha

        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "El usuario no existe",
            "usuario": usuario,
            "captcha": new_captcha,
            "hide_layout": True
        })

    if auth_result == "NO ACTIVO":
        new_captcha = generar_captcha()
        request.session["captcha"] = new_captcha

        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "Usuario no habilitado para usar la aplicación",
            "usuario": usuario,
            "captcha": new_captcha,
            "hide_layout": True
        })

    if auth_result is False:
        new_captcha = generar_captcha()
        request.session["captcha"] = new_captcha

        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_login": "Contraseña incorrecta",
            "usuario": usuario,
            "captcha": new_captcha,
            "hide_layout": True
        })

    # ----------------------
    # 5. LOGIN OK
    # ----------------------
    request.session.clear()

    request.session["user"] = auth_result.usuario
    request.session["user_id"] = auth_result.idUsuario

    auth_result.fechaUltimoLogin = datetime.now()
    service.actualizar_fechaUltimoLogin(auth_result)

    return RedirectResponse("/indexPpal", status_code=302)

def generar_captcha(largo: int = 5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=largo))
    
@router.get("/captcha")
async def captcha(request: Request):

    # ==========================
    # GENERAR CÓDIGO
    # ==========================
    codigo = generar_captcha()

    # Guardar únicamente en sesión
    request.session["captcha"] = codigo

    # ==========================
    # CONFIGURACIÓN
    # ==========================
    WIDTH = 320
    HEIGHT = 110

    # Fondo
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fuente
    try:
        font = ImageFont.truetype("arialbd.ttf", 58)
    except Exception:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 58)
        except Exception:
            font = ImageFont.load_default()

    # ==========================
    # RUIDO DE FONDO
    # ==========================
    for _ in range(1000):
        draw.point(
            (
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT)
            ),
            fill=(
                random.randint(180, 255),
                random.randint(180, 255),
                random.randint(180, 255)
            )
        )

    # ==========================
    # LINEAS DE INTERFERENCIA
    # ==========================
    for _ in range(8):
        draw.line(
            (
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
            ),
            fill=(
                random.randint(120, 180),
                random.randint(120, 180),
                random.randint(120, 180)
            ),
            width=random.randint(1, 3)
        )

    # ==========================
    # TEXTO DISTORSIONADO
    # ==========================
    espacio = 15

    ancho_total = 0

    for letra in codigo:
        bbox = font.getbbox(letra)
        ancho_total += (bbox[2] - bbox[0]) + espacio

    ancho_total -= espacio

    #x = 20
    x = (WIDTH - ancho_total) // 2
    
    for letra in codigo:
        bbox = font.getbbox(letra)
        ancho_letra = bbox[2] - bbox[0]
        
        #angulo = random.randint(-25, 25)
        angulo = random.randint(-5, 5)

        char_img = Image.new("RGBA", (70, 70), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)

        color = (
            random.randint(0, 80),
            random.randint(0, 80),
            random.randint(0, 80)
        )

        draw.text(
            (x, 15),
            letra,
            font=font,
            fill=(0, 0, 0)
        )

        char_img = char_img.rotate(
            angulo,
            expand=True,
            resample=Image.BICUBIC
        )

        y = random.randint(8, 22)

        img.paste(
            char_img,
            (x, y),
            char_img
        )

        #x += random.randint(35, 45)
        x += ancho_letra + espacio

    # ==========================
    # WARP TIPO GOOGLE
    # ==========================
    # Distorsión sinusoidal
    # ==========================
    #Lo dejo comenatdo proque no me gusta pero puede que para alguna otra ocacion sea necesario. 
    '''
    warped = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    

    amplitude = 4
    period = 55

    for y in range(HEIGHT):

        offset = int(
            amplitude *
            math.sin(
                2 * math.pi * y / period
            )
        )

        for x in range(WIDTH):

            nx = x + offset

            if 0 <= nx < WIDTH:
                warped.putpixel(
                    (x, y),
                    img.getpixel((nx, y))
                )
    '''
    warped = img

    # ==========================
    # SUAVIZADO FINAL
    # ==========================
    warped = warped.filter(
        ImageFilter.GaussianBlur(radius=0.5)
    )

    # ==========================
    # EXPORTAR
    # ==========================
    buffer = io.BytesIO()

    warped.save(
        buffer,
        format="PNG",
        optimize=True
    )

    buffer.seek(0)

    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    return Response(
        content=buffer.read(),
        media_type="image/png",
        headers=headers
    )


@router.put("/cambiar-clave", response_model=UsuarioModel)
async def update_clave(
    request: Request,
    usuario_data: dict = Body(...),
    session: Session = Depends(get_session)
):
    
    #validar captcha
    captcha_session = request.session.get("captcha")
    captcha_cambio = usuario_data["captcha_cambio"]

    if not captcha_session or captcha_cambio.upper() != captcha_session:
        captcha_new = generar_captcha()
        request.session["captcha"] = captcha_new

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Captcha incorrecto en cambio de contraseña"}
        )
    
    #validar clave nueva y repeticion
    clave_nueva = usuario_data["clave_nueva"]
       
    usuario = UsuarioModel(
        usuario = usuario_data["usuarioMod"],
        clave = usuario_data["clave_actual"]
    )    
    
    service = UsuarioService(session) 
    usuario = service.authenticate(usuario.usuario, usuario.clave)
    
    if usuario is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Usuario no registrado"}
        )

    if usuario is False:
            
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "La contraseña actual es incorrecta"}
        )
          
    usuario.clave = service.hash_password(clave_nueva)

    usuario=service.actualizar_clave(usuario)  
    
    if not usuario:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Usuario no registrado"}
        )
    
    return usuario


