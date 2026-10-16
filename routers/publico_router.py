import secrets

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from config.conexion import get_session

from models.reclamo_model import ReclamoModel
from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel

from services.localidad_service import LocalidadService
from services.categoria_service import CategoriaService
from services.recurrenciaHecho_service import RecurrenciaHechoService
from services.reclamo_service import ReclamoService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/reclamoVecino")
async def formulario_vecino(request: Request, session: Session = Depends(get_session)):
    loc_service = LocalidadService(session)
    cat_service = CategoriaService(session)
    recur_service = RecurrenciaHechoService(session)

    localidades = loc_service.listar_localidades()
    categorias = cat_service.listar_activas()
    recurrencias = recur_service.listar_recurrencias()

    # Generar token aleatorio criptográficamente seguro
    # Se usa para evitar el envio reiterado del formulario junto con otras tecnikas de seguridad como el captcha
    form_token = secrets.token_hex(16)
    request.session["form_token_valido"] = form_token

    return templates.TemplateResponse(
        "reclamoBromatologia.html",
        {
            "request": request,
            "localidades": localidades,
            "categorias": categorias,
            "recurrencias": recurrencias,
            "form_token": form_token,  # <-- Enviamos el token al HTML
        },
    )
   
@router.post("/reclamo/enviar")
async def registrar_reclamo_post(
    request: Request,
    comercioNombre: Optional[str] = Form(None),
    idLocalidad: int = Form(...),
    calle: str = Form(...),
    latitud: Optional[float] = Form(None),
    longitud: Optional[float] = Form(None),
    categoriaDetalle: Optional[str] = Form(None),
    fechaHoraHecho: str = Form(...),
    frecuencia: str = Form("Primera vez"),
    descripcionProblema: str = Form(...),
    esAnonimo: int = Form(0),
    nomDenunciante: Optional[str] = Form(None),
    apeDenunciante: Optional[str] = Form(None),
    areaCelDenunciante: Optional[int] = Form(None),
    nroCelDenunciante: Optional[int] = Form(None),
    emailDenunciante: Optional[str] = Form(None),
    aceptaDeclaracionJurada: int = Form(1),
    # Datos específicos si involucra alimentos
    productoNombreMarca: Optional[str] = Form(None),
    fechaVencimiento: Optional[str] = Form(None),
    nroLote: Optional[str] = Form(None),
    estadoConservacion: Optional[str] = Form(None),
    evidencias: List[UploadFile] = File([]),
    session: Session = Depends(get_session),
):
    try:
        fecha_hecho = (
            datetime.fromisoformat(fechaHoraHecho)
            if fechaHoraHecho
            else datetime.now()
        )
        es_anonimo_bool = bool(esAnonimo)

        nuevo_reclamo = ReclamoModel(
            comercioNombre=comercioNombre.strip() if comercioNombre else "No especificado",
            idLocalidad=idLocalidad,
            calle=calle.strip(),
            latitud=latitud,
            longitud=longitud,
            categoriaDetalle=categoriaDetalle,
            fechaHoraHecho=fecha_hecho,
            esAnonimo=es_anonimo_bool,
            nomDenunciante=nomDenunciante if not es_anonimo_bool else None,
            apeDenunciante=apeDenunciante if not es_anonimo_bool else None,
            areaCelDenunciante=areaCelDenunciante if not es_anonimo_bool else None,
            nroCelDenunciante=nroCelDenunciante if not es_anonimo_bool else None,
            emailDenunciante=emailDenunciante if not es_anonimo_bool else None,
            aceptaDeclaracionJurada=bool(aceptaDeclaracionJurada),
            idEstadoActual=1,
            idUsuarioCrear=None,
        )

        detalle_alim = None
        if productoNombreMarca and productoNombreMarca.strip():
            detalle_alim = DetalleAlimentoReclamoModel(
                productoNombreMarca=productoNombreMarca.strip(),
                fechaVencimiento=fechaVencimiento if fechaVencimiento else None,
                nroLote=nroLote.strip() if nroLote else None,
                estadoConservacion=estadoConservacion or "",
            )

        service = ReclamoService(session)
        reclamo_guardado = await service.registrar_reclamo_publico(
            reclamo_data=nuevo_reclamo,
            detalle_alimento=detalle_alim,
            archivos_evidencias=evidencias,
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "ok",
                "nroExpediente": reclamo_guardado.nroExpediente,
                "comercio": reclamo_guardado.comercioNombre,
                "esAnonimo": reclamo_guardado.esAnonimo,
                "email": reclamo_guardado.emailDenunciante or "",
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(e)},
        )