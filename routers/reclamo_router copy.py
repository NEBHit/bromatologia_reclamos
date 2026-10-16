import json
import random

from config.security import limiter
from config.conexion import get_session

from fastapi import APIRouter, Depends, Form, Request, status, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models.constante import EstadoReclamoEnum

from models.reclamo_model import ReclamoModel
from models.evidencia_model import EvidenciaModel

from services.reclamo_service import ReclamoService
from services.categoria_service import CategoriaService
from services.estadoReclamo_service import EstadoReclamoService

from utils.mail import enviar_notificacion_expediente
from utils import archivosUpload

router = APIRouter(prefix="/reclamos", tags=["Gestión Interna de Reclamos"])
templates = Jinja2Templates(directory="templates")

#Esquema de datos recibidos desde frontEnd
class ReclamoUpdateSchema(BaseModel): 
    descripcion: Optional[str] = None
    idEstado: Optional[int] = None
    prioridad: Optional[bool] = None


def parsear_hora_comercio(valor_hora: Optional[str]) -> Optional[datetime]:
    #Convierte cadenas tipo '08:30', '08:30:00' 
    
    if not valor_hora or not valor_hora.strip():
        return None
    valor_hora = valor_hora.strip()
    try:
        # Si viene en formato ISO completo
        return datetime.fromisoformat(valor_hora)
    except ValueError:
        pass
    
    try:
        # Si viene en formato 'HH:MM' desde un <input type="time">
        t = datetime.strptime(valor_hora, "%H:%M").time()
        # Se fija una fecha base neutra (ej. 2000-01-01) para satisfacer la columna TIMESTAMP/DATETIME
        return datetime.combine(datetime(2000, 1, 1).date(), t)
    except ValueError:
        pass

    try:
        # Si viene en formato 'HH:MM:SS'
        t = datetime.strptime(valor_hora, "%H:%M:%S").time()
        return datetime.combine(datetime(2000, 1, 1).date(), t)
    except ValueError:
        return None

@router.get("")
async def get_reclamos(request: Request, session: Session = Depends(get_session)):
    
    reclamo_service = ReclamoService(session)
    reclamos = reclamo_service.listar_todos_conEstado()
  
    return templates.TemplateResponse(
        "listar_reclamos.html",
        {
            "request": request,
            "reclamos": reclamos,
        },
    )


@router.get("/{idReclamo:int}/data")
async def get_reclamo_json(
    idReclamo: int,
    session: Session = Depends(get_session)
):
    service = ReclamoService(session)
    reclamo = service.obtener_por_id(idReclamo)

    if not reclamo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Reclamo no encontrado"}
        )

    # Serializamos las evidencias asociadas
    evidencias_lista = []
    if hasattr(reclamo, "evidencias") and reclamo.evidencias:
        for ev in reclamo.evidencias:
            evidencias_lista.append({
                "idEvidencia": getattr(ev, "idEvidencia", None),
                "nombreArchivo": getattr(ev, "nombreArchivo", "Archivo"),
                "rutaAlmacenamiento": getattr(ev, "rutaAlmacenamiento", ""),
                "tipoMime": getattr(ev, "tipoMime", ""),
                "tamanoBytes": getattr(ev, "tamanoBytes", 0)
            })

    # Serializamos categorías asociadas
    categorias_lista = []
    if hasattr(reclamo, "categorias") and reclamo.categorias:
        for c in reclamo.categorias:
            categorias_lista.append({
                "id": getattr(c, "idCategoria", None),
                "nombre": getattr(c, "nombre", getattr(c, "descripcion", "Categoría"))
            })

    data = {
        "idReclamo": reclamo.idReclamo,
        "nroExpediente": reclamo.nroExpediente,
        "comercioNombre": reclamo.comercioNombre or "Sin Nombre de Fantasía",
        "idLocalidad": reclamo.idLocalidad,
        "localidadNombre": reclamo.localidad.nombre if hasattr(reclamo, "localidad") and reclamo.localidad else None,
        "calle": reclamo.calle,
        "areaCelComercio": reclamo.areaCelComercio,
        "nroCelComercio": reclamo.nroCelComercio,
        "horaApertura": reclamo.horaAperturaComercio.strftime("%H:%M") if reclamo.horaAperturaComercio else None,
        "horaCierre": reclamo.horaCierreComercio.strftime("%H:%M") if reclamo.horaCierreComercio else None,
        "latitud": reclamo.latitud,
        "longitud": reclamo.longitud,
        
        "categorias": categorias_lista,
        "categoriaDetalle": reclamo.categoriaDetalle,

        "prioridad": reclamo.prioridad,
        "idEstadoActual": reclamo.idEstadoActual,
        "fechaHoraHecho": reclamo.fechaHoraHecho.strftime("%d/%m/%Y %H:%M") if reclamo.fechaHoraHecho else None,
        "idRecurrenciaHecho": reclamo.idRecurrenciaHecho,
        "incidenteHecho": reclamo.incidenteHecho,

        "esAnonimo": reclamo.esAnonimo,
        "nomDenunciante": reclamo.nomDenunciante,
        "apeDenunciante": reclamo.apeDenunciante,
        "areaCelDenunciante": reclamo.areaCelDenunciante,
        "nroCelDenunciante": reclamo.nroCelDenunciante,
        "emailDenunciante": reclamo.emailDenunciante,

        "evidencias": evidencias_lista
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

# ==========================================
# 1. RUTA ESTÁTICA /exito (PRIMERO)
# ==========================================
@router.get("/exito")
async def reclamo_exito_view(
    request: Request,
    expte: Optional[str] = Query(default=None)
):
    return templates.TemplateResponse(
        "reclamo_exito.html",
        {
            "request": request,
            "nro_expediente": expte or "BRO-S/N"
        }
    )

@router.get("/captcha-code")
async def obtener_codigo_captcha(request: Request):
  """Genera el código de seguridad, lo guarda en la sesión y lo envía al front."""
  caracteres = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
  codigo = "".join(random.choices(caracteres, k=6))
  request.session["captcha_valido"] = codigo
  return {"codigo": codigo}


# ==========================================
# 2. RUTA DINÁMICA /{idReclamo} (DESPUÉS)
# ==========================================
'''@router.get("/{idReclamo:int}")
async def get_detalle_reclamo(
    idReclamo: int,
    request: Request,
    session: Session = Depends(get_session),
):
    service = ReclamoService(session)
    reclamo = service.obtener_por_id(idReclamo)

    if not reclamo:
        return RedirectResponse("/reclamos", status_code=303)

    return templates.TemplateResponse(
        "detalle_reclamo.html",
        {
            "request": request,
            "reclamo": reclamo,
            "detalle_alimento": reclamo.detalle_alimento,
            "evidencias": reclamo.evidencias,
            "historial": reclamo.historial,
        },
    )
'''

'''@router.post("/cambiar_estado")
async def cambiar_estado_reclamo(
    request: Request,
    idReclamo: int = Form(...),
    idEstadoNuevo: int = Form(...),
    observaciones: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    id_usuario_actual = request.session.get("user_id", 1)
    service = ReclamoService(session)

    reclamo_act = service.cambiar_estado(
        id_reclamo=idReclamo,
        nuevo_estado_id=idEstadoNuevo,
        id_usuario=id_usuario_actual,
        observaciones=observaciones,
    )

    if not reclamo_act:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Reclamo no encontrado"},
        )

    return RedirectResponse(f"/reclamos/{idReclamo}", status_code=303)
'''

@router.put("/{idReclamo}")
async def actualizar_reclamo(
    idReclamo: int,
    datos: ReclamoUpdateSchema,
    request: Request,
    session: Session = Depends(get_session),
):
    service = ReclamoService(session)
    reclamo = service.obtener_por_id(idReclamo)

    if not reclamo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Reclamo no encontrado"},
        )

    try:
        id_usuario = request.session.get("user_id", 1)

        # 1. Descripción / Incidente
        if datos.descripcion is not None:
            reclamo.incidenteHecho = datos.descripcion.strip()

        # 2. Prioridad
        if datos.prioridad is not None:
            reclamo.prioridad = datos.prioridad

        # 3. Estado
        if datos.idEstado is not None:
            reclamo.idEstadoActual = datos.idEstado

        reclamo.idUsuarioModificar = id_usuario
        reclamo.fechaMod = datetime.now()

        service = ReclamoService(session)
        reclamo = service.actualizar_reclamo(idReclamo)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Reclamo actualizado correctamente"},
        )

    except Exception as error:
        session.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Error al actualizar: {str(error)}"},
        )

@router.delete("/{idReclamo}")
async def delete_reclamo(
    idReclamo: int, session: Session = Depends(get_session)
):
    service = ReclamoService(session)
    exito = service.eliminar_reclamo(idReclamo)

    if exito == "no existe":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Reclamo no encontrado"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Reclamo eliminado correctamente"},
        )


# Router público sin prefijo para el formulario de vecinos
public_router = APIRouter(tags=["Portal Vecino"])

# Si tu router tiene prefix="/reclamos", en el form de HTML la ruta debe ser /reclamos/reclamoVecino
# O bien puedes declarar la ruta sin prefix directamente
@router.post("/reclamoVecino")
@limiter.limit("5/minute")
async def registrar_reclamo_vecino(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    
    #Datos del Comercio
    comercioNombre: Optional[str] = Form(None),
    idLocalidad: int = Form(...),
    calle: str = Form(...),
    areaCelComercio: Optional[str] = Form(None),
    nroCelComercio: Optional[str] = Form(None),
    horaAperturaComercio: Optional[str] = Form(None),
    horaCierreComrcio: Optional[str] = Form(None),  
    latitud: Optional[str] = Form(None),
    longitud: Optional[str] = Form(None),

    #Categorías
    categoriasJson: str = Form(...),
    categoriaDetalle: Optional[str] = Form(None),

    #Detalle del Alimento (opcionales) solo se cargan si se selcciono la categoria 1 o 2
    productoNombreMarca: Optional[str] = Form(None),
    fechaVencimiento: Optional[str] = Form(None),
    nroLote: Optional[str] = Form(None),
    estadoConservacion: Optional[str] = Form(None),

    #Detalle del Hecho
    prioridad: Optional[str] = Form(None),
    fechaHoraHecho: str = Form(...),
    idRecurrenciaHecho: Optional[str] = Form(None),
    incidenteHecho: Optional[str] = Form(None),

    #Archivos de evidencias
    evidencias: List[UploadFile] = File(default=[]),

    #Denunciante
    esAnonimo: str = Form(...),
    nomDenunciante: Optional[str] = Form(None),
    apeDenunciante: Optional[str] = Form(None),
    areaCelDenunciante: Optional[str] = Form(None),
    nroCelDenunciante: Optional[str] = Form(None),
    emailDenunciante: Optional[str] = Form(None),

    #Declaración Jurada y Captcha
    aceptaDeclaracionJurada: Optional[str] = Form(None),
    form_token: Optional[str] = Form(None),
    captchaInput: Optional[str] = Form(None),
):
    try:
        # VERIFICAR EL TOKEN (Solo lectura, NO QUEMAR AÚN)
        token_sesion = request.session.get("form_token_valido")
        if not form_token or not token_sesion or form_token != token_sesion:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "detail": "Este trámite ya fue completado. Si desea ingresar un nuevo reclamo, recargue la página."
                }
            )
        
        # VERIFICAR EL CAPTCHA CONTRA LA SESIÓN 
        codigo_sesion = request.session.get("captcha_valido")
        if (
            not captchaInput
            or not codigo_sesion
            or captchaInput.strip().upper() != codigo_sesion.upper()
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "detail": (
                        "El código de seguridad ingresado es incorrecto o expiró."
                        " Intente nuevamente."
                    ),
                },
            )
        # Consumir el captcha para evitar reutilización
        request.session.pop("captcha_valido", None)

        # Conversiones numéricas seguras
        area_comercio_int = int(areaCelComercio) if areaCelComercio and areaCelComercio.isdigit() else None
        nro_comercio_int = int(nroCelComercio) if nroCelComercio and nroCelComercio.isdigit() else None
        
        area_denun_int = int(areaCelDenunciante) if areaCelDenunciante and areaCelDenunciante.isdigit() else None
        nro_denun_int = int(nroCelDenunciante) if nroCelDenunciante and nroCelDenunciante.isdigit() else None
        
        lat_float = float(latitud) if latitud and latitud.strip() else None
        lon_float = float(longitud) if longitud and longitud.strip() else None

        recurrencia_int = int(idRecurrenciaHecho) if idRecurrenciaHecho and idRecurrenciaHecho.isdigit() else None

        # Parsear horarios de apertura y cierre
        dt_apertura = parsear_hora_comercio(horaAperturaComercio)
        dt_cierre = parsear_hora_comercio(horaCierreComrcio)

        # Parsear categorías
        categorias_db = []

        #Ver qué llega exactamente en el campo Form
        #print(f"\n--- [DEBUG] Raw categoriasJson: {repr(categoriasJson)} ---")

        if categoriasJson and categoriasJson.strip():
            categorias_data = json.loads(categoriasJson) if categoriasJson else []
         
            # Asegurar que sea una lista
            if isinstance(categorias_data, list):
                ids_categorias = []
                for c in categorias_data:
                    val = c.get("idCategoria") if isinstance(c, dict) else c
                    try:
                        if val is not None:
                            ids_categorias.append(int(val))
                    except (ValueError, TypeError) as err:
                        continue

                # Eliminar duplicados manteniendo orden
                ids_categorias = list(dict.fromkeys(ids_categorias))
                
                # Ver los IDs limpios que se mandan al servicio
                #print(f"[DEBUG] IDs extraídos finales: {ids_categorias}")

                if ids_categorias:
                    categoria_service = CategoriaService(session)
                    categorias_db = categoria_service.listar_categoriasSoloSeleccionadas(ids_categorias)
                
        # Determinar flag anónimo
        es_anonimo_bool = str(esAnonimo).strip().lower() in ("true", "1", "yes")

        prioridad_bool = str(prioridad).strip().lower() in ("true", "1", "on", "yes")

        # Parsear fecha del hecho
        try:
            fecha_hecho_dt = datetime.fromisoformat(fechaHoraHecho)
        except (ValueError, TypeError):
            fecha_hecho_dt = datetime.now()

       
        # Procesar Detalle Alimento a list[dict]
        # Si se agregá un campo Form detalleAlimentoJson en el endpoint, parsealo acá.
        # Por ahora dejamos la lista lista para el service:
        detalle_alimento_lista_dict: list[dict] = []

        # Se verifica si al menos cargó el nombre del producto o alguno de los campos
        tiene_datos_alimento = any([
            productoNombreMarca and productoNombreMarca.strip(),
            fechaVencimiento and fechaVencimiento.strip(),
            nroLote and nroLote.strip(),
            estadoConservacion and estadoConservacion.strip()
        ])

        if tiene_datos_alimento:
            # Parsear fecha de vencimiento si viene con valor
            fecha_venc_parsed = None
            if fechaVencimiento and fechaVencimiento.strip():
                try:
                    # El input type="date" envía siempre formato YYYY-MM-DD
                    fecha_venc_parsed = datetime.strptime(fechaVencimiento.strip(), "%Y-%m-%d").date()
                except ValueError:
                    fecha_venc_parsed = None

            item_alimento = {
                "productoNombreMarca": productoNombreMarca.strip() if productoNombreMarca else None,
                "fechaVencimiento": fecha_venc_parsed,  # o fechaVencimiento.strip() si tu modelo usa string
                "nroLote": nroLote.strip() if nroLote else None,
                "estadoConservacion": estadoConservacion.strip() if estadoConservacion else None,
            }
            detalle_alimento_lista_dict.append(item_alimento)

        print(f"[DEBUG] Detalle Alimento procesado: {detalle_alimento_lista_dict}")

        # Filtrar archivos de evidencias válidos
        archivos_validos = [f for f in evidencias if f.filename and f.filename.strip()]

        # Generar número de expediente
        anio = datetime.now().year
        num_aleatorio = random.randint(1000, 9999)
        nro_expediente = f"EXP-BROM-{anio}-{num_aleatorio}"

        # Obtener usuario de sesión de forma segura (None si es vecino público)
        usuario_actual = request.session.get("user_id")

        # Crear instancia del ReclamoModel
        nuevo_reclamo_instancia = ReclamoModel(
            nroExpediente=nro_expediente,
            comercioNombre=comercioNombre.strip() if comercioNombre and comercioNombre.strip() else "Sin Nombre de Fantasía",
            idLocalidad=idLocalidad,
            calle=calle.strip(),
            latitud=lat_float,
            longitud=lon_float,
            areaCelComercio=area_comercio_int,
            nroCelComercio=nro_comercio_int,
            horaAperturaComercio=dt_apertura,
            horaCierreComercio=dt_cierre,
            categoriaDetalle=categoriaDetalle.strip() if categoriaDetalle else None,
            prioridad=prioridad_bool,
            fechaHoraHecho=fecha_hecho_dt,
            idRecurrenciaHecho=recurrencia_int,
            incidenteHecho=incidenteHecho.strip() if incidenteHecho else None,
            esAnonimo=es_anonimo_bool,
            nomDenunciante=None if es_anonimo_bool else (nomDenunciante.strip() if nomDenunciante else None),
            apeDenunciante=None if es_anonimo_bool else (apeDenunciante.strip() if apeDenunciante else None),
            areaCelDenunciante=None if es_anonimo_bool else area_denun_int,
            nroCelDenunciante=None if es_anonimo_bool else nro_denun_int,
            emailDenunciante=None if es_anonimo_bool else (emailDenunciante.strip() if emailDenunciante else None),
            aceptaDeclaracionJurada=bool(aceptaDeclaracionJurada),
            idEstadoActual=EstadoReclamoEnum.RECIBIDO,
            idUsuarioCrear=usuario_actual,
            idUsuarioModificar=usuario_actual,
            fechaMod=datetime.now()
        )

        # 7. LLAMADA AL SERVICE (con await respetando su firma exacta)
        service = ReclamoService(session)
        nuevo_reclamo = await service.nuevo_reclamo_publico(
            nuevo_Reclamo=nuevo_reclamo_instancia,
            detalleAlimento=detalle_alimento_lista_dict,
            categorias=categorias_db,
            archivos_evidencias=archivos_validos
        )
               

        # Enviar correo solo si no es anónimo y tiene email válido
        # --- FILTRO ANTI HEADER-INJECTION Y DISPARO DE CORREO ---
        # -------------------------------------------------------------
        if not es_anonimo_bool and emailDenunciante:
            email_limpio = emailDenunciante.strip()
            # Prevenir inyección de saltos de línea (CRLF) en cabeceras SMTP
            if (
                "\r" not in email_limpio
                and "\n" not in email_limpio
                and "@" in email_limpio
            ):
                nombre_vecino = (
                    f"{nomDenunciante or ''} {apeDenunciante or ''}".strip()
                    or "Vecino/a"
                )
                comercio_referencia = (
                    nuevo_reclamo.comercioNombre or nuevo_reclamo.calle
                )

                background_tasks.add_task(
                    enviar_notificacion_expediente,
                    destinatario=email_limpio,
                    nombre_completo=nombre_vecino,
                    nro_expediente=nuevo_reclamo.nroExpediente,
                    comercio=comercio_referencia,
                    descripcion=incidenteHecho or "Sin descripción detallada",
                )
       
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "ok",
                "nroExpediente": nuevo_reclamo.nroExpediente,
                "mensaje": "Reclamo generado exitosamente",
                "redirect": f"/reclamos/exito?expte={nuevo_reclamo.nroExpediente}"
            }
        )

    except Exception as error:
        session.rollback()
        print(f"[ERROR BACKEND RECLAMO]: {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": str(error)}
        )

