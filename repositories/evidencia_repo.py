from typing import List, Optional
from sqlmodel import Session, select
from models.evidencia_model import EvidenciaModel


def get_by_id(session: Session, id_evidencia: int) -> Optional[EvidenciaModel]:
    return session.get(EvidenciaModel, id_evidencia)


def get_by_reclamo_id(session: Session, id_reclamo: int) -> List[EvidenciaModel]:
    return session.exec(
        select(EvidenciaModel).where(EvidenciaModel.reclamo_id == id_reclamo)
    ).all()


def create(session: Session, evidencia: EvidenciaModel) -> EvidenciaModel:
    session.add(evidencia)
    session.commit()
    session.refresh(evidencia)
    return evidencia


def delete(session: Session, evidencia: EvidenciaModel):
    session.delete(evidencia)
    session.commit()