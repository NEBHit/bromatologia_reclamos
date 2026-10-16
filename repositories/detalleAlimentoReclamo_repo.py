from typing import Optional
from sqlmodel import Session, select
from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel


def get_by_id(session: Session, id_detalle: int) -> Optional[DetalleAlimentoReclamoModel]:
    return session.get(DetalleAlimentoReclamoModel, id_detalle)


def get_by_reclamo_id(session: Session, id_reclamo: int) -> Optional[DetalleAlimentoReclamoModel]:
    return session.exec(
        select(DetalleAlimentoReclamoModel).where(
            DetalleAlimentoReclamoModel.idReclamo == id_reclamo
        )
    ).first()


def create(session: Session, detalle: DetalleAlimentoReclamoModel) -> DetalleAlimentoReclamoModel:
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle


def update(session: Session, detalle: DetalleAlimentoReclamoModel) -> DetalleAlimentoReclamoModel:
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle


def delete(session: Session, detalle: DetalleAlimentoReclamoModel):
    session.delete(detalle)
    session.commit()