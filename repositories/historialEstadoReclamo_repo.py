from typing import List, Optional
from sqlmodel import Session, select
from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel


def get_by_id(session: Session, id_historial: int) -> Optional[HistorialEstadoReclamoModel]:
    return session.get(HistorialEstadoReclamoModel, id_historial)


def get_by_reclamo_id(session: Session, id_reclamo: int) -> List[HistorialEstadoReclamoModel]:
    return session.exec(
        select(HistorialEstadoReclamoModel)
        .where(HistorialEstadoReclamoModel.idReclamo == id_reclamo)
        .order_by(HistorialEstadoReclamoModel.fechaMod.asc())
    ).all()


def create(session: Session, historial: HistorialEstadoReclamoModel) -> HistorialEstadoReclamoModel:
    session.add(historial)
    session.commit()
    session.refresh(historial)
    return historial


def delete(session: Session, historial: HistorialEstadoReclamoModel):
    session.delete(historial)
    session.commit()