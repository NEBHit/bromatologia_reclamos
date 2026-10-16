from typing import Optional
from sqlmodel import Session, select
from models.reclamoCategoria_model import ReclamoCategoriaModel


def get_by_id(session: Session, id_detalle: int) -> Optional[ReclamoCategoriaModel]:
    return session.get(ReclamoCategoriaModel, id_detalle)


def get_by_reclamo_id(session: Session, id_reclamo: int) -> Optional[ReclamoCategoriaModel]:
    return session.exec(
        select(ReclamoCategoriaModel).where(
            ReclamoCategoriaModel.idReclamo == id_reclamo
        )
    ).first()


def create(session: Session, detalle: ReclamoCategoriaModel) -> ReclamoCategoriaModel:
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle


def update(session: Session, detalle: ReclamoCategoriaModel) -> ReclamoCategoriaModel:
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle


def delete(session: Session, detalle: ReclamoCategoriaModel):
    session.delete(detalle)
    session.commit()