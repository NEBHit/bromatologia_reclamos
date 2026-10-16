from sqlmodel import Session, select
from models.inspector_model import InspectorModel
from typing import List, Optional

def get_all(session: Session) -> List[InspectorModel]:
    return session.exec(select(InspectorModel).order_by(InspectorModel.apellido)).all()

def get_by_id(session: Session, id: int) -> Optional[InspectorModel]:
    return session.get(InspectorModel, id)

def create(session: Session, inspector: InspectorModel) -> InspectorModel:
    session.add(inspector)
    session.commit()
    session.refresh(inspector)
    return inspector

def update(session: Session, inspector: InspectorModel) -> InspectorModel:
    session.add(inspector)
    session.commit()
    session.refresh(inspector)
    return inspector

def delete(session: Session, inspector: InspectorModel):
    session.delete(inspector)
    session.commit()