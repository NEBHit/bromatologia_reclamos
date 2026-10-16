from typing import List
from fastapi import APIRouter, Depends, Body, Form, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from config.conexion import get_session
from models.recurrenciaHecho_model import RecurrenciaHechoModel
from services.recurrenciaHecho_service import RecurrenciaHechoService

router = APIRouter(prefix="/localidades", tags=["Localidades"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_model=List[ RecurrenciaHechoModel])
async def get_recurrencias(request: Request, session: Session = Depends(get_session)):
    service =  RecurrenciaHechoService(session)
    recurrencias = service.listar_recurrencias()

    return templates.TemplateResponse(
        "listar_recurrencias.html",
        {"request": request, "recurrencias": recurrencias},
    )


@router.post("/agregar", response_model= RecurrenciaHechoModel)
async def agregar_recurrencia_post(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    session: Session = Depends(get_session),
):
    nueva_recurrencia =  RecurrenciaHechoModel(nombre=nombre, descripcion=descripcion)
    service =  RecurrenciaHechoService(session)
    service.crear_recurrencia(nueva_recurrencia)

    return RedirectResponse("/recurrencias", status_code=303)


@router.put("/{idRecurrenciaHecho}", response_model= RecurrenciaHechoModel)
async def update_recurrencia(
    idRecurrenciaHecho: int,
    recurrencia_data: dict = Body(...),
    session: Session = Depends(get_session),
):
    service =  RecurrenciaHechoService(session)
    recurrencia = service.obtener_por_id(idRecurrenciaHecho)
    if not recurrencia:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Recuerrencia no encontrada"},
        )

    recurrencia.nombre = recurrencia_data["nombre"]
    recurrencia.codPostal = recurrencia_data.get("descripcion")
    service.actualizar_recurrencia(recurrencia)

    return recurrencia


@router.delete("/{idRecurrenciaHecho}")
async def delete_localidad(
    idRecurrenciaHecho: int, session: Session = Depends(get_session)
):
    service =  RecurrenciaHechoService(session)
    exito = service.eliminar_localidad(idRecurrenciaHecho)

    if exito == "no existe":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Recurrencia no encontrada"},
        )
    elif exito == "relacionado":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": (
                    "No se puede eliminar la Recurrencia porque tiene reclamos asociados"
                )
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Recurrencia eliminada exitosamente"},
        )