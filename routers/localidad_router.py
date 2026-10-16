from typing import List
from fastapi import APIRouter, Depends, Body, Form, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from config.conexion import get_session
from models.localidad_model import LocalidadModel
from services.localidad_service import LocalidadService

router = APIRouter(prefix="/localidades", tags=["Localidades"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_model=List[LocalidadModel])
async def get_localidades(request: Request, session: Session = Depends(get_session)):
    service = LocalidadService(session)
    localidades = service.listar_localidades()

    return templates.TemplateResponse(
        "listar_localidades.html",
        {"request": request, "localidades": localidades},
    )


@router.post("/agregar", response_model=LocalidadModel)
async def agregar_localidad_post(
    nombre: str = Form(...),
    codPostal: int = Form(None),
    session: Session = Depends(get_session),
):
    nueva_localidad = LocalidadModel(nombre=nombre, codPostal=codPostal)
    service = LocalidadService(session)
    service.crear_localidad(nueva_localidad)

    return RedirectResponse("/localidades", status_code=303)


@router.put("/{idLocalidad}", response_model=LocalidadModel)
async def update_localidad(
    idLocalidad: int,
    localidad_data: dict = Body(...),
    session: Session = Depends(get_session),
):
    service = LocalidadService(session)
    localidad = service.obtener_por_id(idLocalidad)
    if not localidad:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Localidad no encontrada"},
        )

    localidad.nombre = localidad_data["nombre"]
    localidad.codPostal = localidad_data.get("codPostal")
    service.actualizar_localidad(localidad)

    return localidad


@router.delete("/{idLocalidad}")
async def delete_localidad(
    idLocalidad: int, session: Session = Depends(get_session)
):
    service = LocalidadService(session)
    exito = service.eliminar_localidad(idLocalidad)

    if exito == "no existe":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Localidad no encontrada"},
        )
    elif exito == "relacionado":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": (
                    "No se puede eliminar la localidad porque tiene reclamos asociados"
                )
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Localidad eliminada exitosamente"},
        )