from typing import List, Optional
from sqlmodel import Session, select
from models.categoria_model import CategoriaModel


def get_all(session: Session) -> List[CategoriaModel]:
    return session.exec(
        select(CategoriaModel).order_by(CategoriaModel.orden)
    ).all()

def get_all_idsSelect(session: Session, ids: List[int]) -> List[CategoriaModel]:
    if not ids:
        return []
        
    statement = select(CategoriaModel).where(CategoriaModel.idCategoria.in_(ids))
    return session.exec(statement).all()

def get_activas(session: Session) -> List[CategoriaModel]:
    return session.exec(
        select(CategoriaModel)
        .where(CategoriaModel.activa == True)
        .order_by(CategoriaModel.orden)
    ).all()


def get_by_id(session: Session, id_categoria: int) -> Optional[CategoriaModel]:
    return session.get(CategoriaModel, id_categoria)


def create(session: Session, categoria: CategoriaModel) -> CategoriaModel:
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def update(session: Session, categoria: CategoriaModel) -> CategoriaModel:
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def delete(session: Session, categoria: CategoriaModel):
    session.delete(categoria)
    session.commit()