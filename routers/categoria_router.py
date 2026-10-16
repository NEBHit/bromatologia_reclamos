from typing import List
from fastapi import APIRouter, Depends, Body, Form, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from config.conexion import get_session
from models.categoria_model import CategoriaModel
from services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorías de Reclamo"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_model=List[CategoriaModel])
async def get_categorias(request: Request, session: Session = Depends(get_session)):
    service = CategoriaService(session)
    categorias = service.listar_categorias()

    return templates.TemplateResponse(
        "listar_categorias.html",
        {"request": request, "categorias": categorias},
    )


@router.post("/agregar", response_model=CategoriaModel)
async def agregar_categoria_post(
    nombre: str = Form(...),
    requiereDetalle: bool = Form(False),
    orden: int = Form(0),
    session: Session = Depends(get_session),
):
    nueva_cat = CategoriaModel(
        nombre=nombre,
        requiereDetalle=requiereDetalle,
        orden=orden,
        activa=True,
    )
    service = CategoriaService(session)
    service.crear_categoria(nueva_cat)

    return RedirectResponse("/categorias", status_code=303)


@router.put("/{idCategoria}", response_model=CategoriaModel)
async def update_categoria(
    idCategoria: int,
    categoria_data: dict = Body(...),
    session: Session = Depends(get_session),
):
    service = CategoriaService(session)
    cat = service.obtener_por_id(idCategoria)
    if not cat:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Categoría no encontrada"},
        )

    cat.nombre = categoria_data["nombre"]
    cat.requiereDetalle = categoria_data.get("requiereDetalle", False)
    cat.orden = categoria_data.get("orden", 0)
    cat.activa = categoria_data.get("activa", True)

    service.actualizar_categoria(cat)
    return cat


@router.delete("/{idCategoria}")
async def delete_categoria(
    idCategoria: int, session: Session = Depends(get_session)
):
    service = CategoriaService(session)
    exito = service.eliminar_categoria(idCategoria)

    if exito == "no existe":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Categoría no encontrada"},
        )
    elif exito == "relacionado":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": (
                    "No se puede eliminar la categoría porque existen reclamos"
                    " registrados bajo la misma"
                )
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Categoría eliminada exitosamente"},
        )