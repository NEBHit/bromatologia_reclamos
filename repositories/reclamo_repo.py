from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select

from models.reclamo_model import ReclamoModel
from models.estadoReclamo_model import EstadoReclamoModel
from models.categoria_model import CategoriaModel
from models.reclamoCategoria_model import ReclamoCategoriaModel
from models.evidencia_model import EvidenciaModel
from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel
from models.localidad_model import LocalidadModel
from models.inspector_model import InspectorModel

def get_all(session: Session) -> List[ReclamoModel]:
    return session.exec(
        select(ReclamoModel).order_by(ReclamoModel.fechaIngresoSistema.desc())
    ).all()

def get_all_Estado(session: Session):
    stmt = (
        select(
            ReclamoModel,
            EstadoReclamoModel.nombre,
            EstadoReclamoModel.colorBadge  # <-- SELECCIONAMOS EL COLOR
        )
        .outerjoin(
            EstadoReclamoModel,
            EstadoReclamoModel.idEstadoReclamo == ReclamoModel.idEstadoActual
        )
        .order_by(ReclamoModel.fechaIngresoSistema.desc())
    )

    resultados = session.exec(stmt).all()

    lista = []
    for reclamo, nombre_estado, color_badge in resultados:
        item = reclamo.model_dump()
        item["nombreEstado"] = nombre_estado or "Sin Estado"
        item["colorBadge"] = color_badge or "bg-secondary text-white"  # <-- INCLUIMOS EN EL DICT
        lista.append(item)

    return lista

def get_by_id(session: Session, id_reclamo: int) -> Optional[ReclamoModel]:
    return session.get(ReclamoModel, id_reclamo)

def get_localidad_reclamo(session: Session, idLocalidad: int) -> Optional[LocalidadModel]:
    return session.get(LocalidadModel, idLocalidad)

def get_categorias_reclamo(session: Session, idReclamo: int):
    """Obtiene las categorías asociadas al reclamo mediante la tabla intermedia."""
    stmt = (
        select(CategoriaModel)
        .join(
            ReclamoCategoriaModel,
            CategoriaModel.idCategoria == ReclamoCategoriaModel.idCategoria
        )
        .where(ReclamoCategoriaModel.idReclamo == idReclamo)
    )
    return session.exec(stmt).all()

def get_evidencias_reclamo(session: Session, idReclamo: int) -> List[EvidenciaModel]:
    """Obtiene todas las evidencias cargadas para un reclamo."""
    stmt = (
        select(EvidenciaModel)
        .where(EvidenciaModel.idReclamo == idReclamo)
    )
    return session.exec(stmt).all()

def get_detalle_alimento_reclamo(session: Session, idReclamo: int) -> Optional[DetalleAlimentoReclamoModel]:
    """Obtiene el detalle del alimento si fue cargado para este reclamo."""
    stmt = (
        select(DetalleAlimentoReclamoModel)
        .where(DetalleAlimentoReclamoModel.idReclamo == idReclamo)
    )
    return session.exec(stmt).first()

def get_inspector_reclamo(session: Session, idInpector: int) -> Optional[InspectorModel]:
    return session.get(InspectorModel, idInpector)

def get_by_expediente(session: Session, nro_expediente: str) -> Optional[ReclamoModel]:
    return session.exec(
        select(ReclamoModel).where(ReclamoModel.nroExpediente == nro_expediente)
    ).first()


def get_by_estado(session: Session, id_estado: int) -> List[ReclamoModel]:
    return session.exec(
        select(ReclamoModel)
        .where(ReclamoModel.idEstadoActual == id_estado)
        .order_by(ReclamoModel.fechaIngresoSistema.desc())
    ).all()

def buscar_duplicado_reciente(session: Session, calle: str, minutos: int = 2) -> Optional[ReclamoModel]:
    #Busca si existe un reclamo registrado recientemente para la misma dirección.
    
    tiempo_limite = datetime.now() - timedelta(minutes=minutos)
        
    statement = select(ReclamoModel).where(
            ReclamoModel.calle == calle.strip(),
            ReclamoModel.fechaMod >= tiempo_limite
        )
    return session.exec(statement).first()

def create(session: Session, reclamo: ReclamoModel) -> ReclamoModel:
    session.add(reclamo)
    session.commit()
    session.refresh(reclamo)
    return reclamo


def update(session: Session, reclamo: ReclamoModel) -> ReclamoModel:
    session.add(reclamo)
    session.commit()
    session.refresh(reclamo)
    return reclamo


def delete(session: Session, reclamo: ReclamoModel):
    session.delete(reclamo)
    session.commit()