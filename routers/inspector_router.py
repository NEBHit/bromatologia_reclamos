from fastapi import APIRouter, Depends, Body, Form, Request,status
from typing import List
from sqlmodel import Session
from fastapi.responses import RedirectResponse,JSONResponse
from config.conexion import get_session
from fastapi.templating import Jinja2Templates

from models.inspector_model import InspectorModel
from services.inspector_service import InspectorService


router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/inspectores", response_model=List[InspectorModel])
async def get_inspectores(request: Request, session: Session = Depends(get_session)):
    service = InspectorService(session)  
    inspectores = service.listar_inspectores() 

    return templates.TemplateResponse("listar_inspectores.html", { 
        "request": request,
        "inspectores": inspectores
    })

@router.get("/agregar_inspector", response_model=InspectorModel)
async def agregar_inspector_get(nombre: str = Form(...), apellido: str = Form(...), session: Session = Depends(get_session)):

    service = InspectorService(session)  
    inspectores = service.crear_inspector(nombre, apellido) 

    return RedirectResponse("/inspectores", status_code=303)
                                      
@router.post("/agregar_inspector", response_model=InspectorModel)
async def agregar_inspector_post(
    request: Request,
    nombre : str = Form(...),
    apellido: str = Form(...),
    session: Session = Depends(get_session)
):
    nuevo_inspector = InspectorModel(
        nombre=nombre,
        apellido=apellido,
        idUsuarioCrear=request.session["user_id"]
    )
    
    service = InspectorService(session)
    service.crear_inspector(nuevo_inspector)
    
    return RedirectResponse("/inspectores", status_code=303)

@router.put("/inspector/{idInspector}", response_model=InspectorModel)
async def update_inspector(
    idInspector: int,
    inspector_data: dict = Body(...),
    session: Session = Depends(get_session)
):
    inspector = session.get(InspectorModel, idInspector)
    if not inspector:
        return {"error": "Inspector no encontrado"}
    
    inspector.nombre = inspector_data["nombre"]
    inspector.apellido = inspector_data.get("apellido", "")
    
    service = InspectorService(session)
    service.actualizar_inspector(inspector)
        
    return inspector

@router.delete("/inspector/{idInspector}")
async def delete_inspector(
    idInspector: int,
    session: Session = Depends(get_session)
):
    service = InspectorService(session)
    exito = service.eliminar_inspector(idInspector)

    if exito == "no existe":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Inspector no encontrado"}
        )
    elif exito == "relacionado":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "No se puede eliminar el Inspector porque está asignado a algún expediente"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Inspector eliminado exitosamente"}
        )

