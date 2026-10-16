from typing import List, Optional
from sqlmodel import Session, select
from models.localidad_model import LocalidadModel


def get_all(session: Session) -> List[LocalidadModel]:
    return session.exec(select(LocalidadModel).order_by(LocalidadModel.nombre)).all()


def get_by_id(session: Session, idLocalidad: int) -> Optional[LocalidadModel]:
    return session.get(LocalidadModel, idLocalidad)


def create(session: Session, localidad: LocalidadModel) -> LocalidadModel:
    session.add(localidad)
    session.commit()
    session.refresh(localidad)
    return localidad


def update(session: Session, localidad: LocalidadModel) -> LocalidadModel:
    session.add(localidad)
    session.commit()
    session.refresh(localidad)
    return localidad


def delete(session: Session, localidad: LocalidadModel):
    session.delete(localidad)
    session.commit()