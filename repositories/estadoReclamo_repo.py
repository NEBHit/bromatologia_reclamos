from typing import List, Optional
from sqlmodel import Session, select
from models.estadoReclamo_model import EstadoReclamoModel


def get_all(session: Session) -> List[EstadoReclamoModel]:
    return session.exec(select(EstadoReclamoModel).order_by(EstadoReclamoModel.idEstadoReclamo)).all()


def get_by_id(session: Session, id_estado: int) -> Optional[EstadoReclamoModel]:
    return session.get(EstadoReclamoModel, id_estado)


def create(session: Session, estado: EstadoReclamoModel) -> EstadoReclamoModel:
    session.add(estado)
    session.commit()
    session.refresh(estado)
    return estado


def update(session: Session, estado: EstadoReclamoModel) -> EstadoReclamoModel:
    session.add(estado)
    session.commit()
    session.refresh(estado)
    return estado


def delete(session: Session, estado: EstadoReclamoModel):
    session.delete(estado)
    session.commit()