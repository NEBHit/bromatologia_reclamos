
from sqlmodel import Session, select
from models.usuario_model import UsuarioModel
from typing import Optional

def get_by_idUsuario(session: Session, id: int) -> Optional[UsuarioModel]:
    return session.get(UsuarioModel, id)

def get_by_usuarioName(session: Session, usuario: str):
    return session.exec(select(UsuarioModel).filter(UsuarioModel.usuario == usuario)).first()

def update(session: Session, user: UsuarioModel) -> UsuarioModel:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user