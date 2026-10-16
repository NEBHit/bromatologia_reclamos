from typing import List, Optional
from sqlmodel import Session, select
from models.recurrenciaHecho_model import  RecurrenciaHechoModel


def get_all(session: Session) -> List[ RecurrenciaHechoModel]:
    return session.exec(select( RecurrenciaHechoModel).order_by( RecurrenciaHechoModel.orden)).all()


def get_by_id(session: Session, idRecurrenciaHecho: int) -> Optional[ RecurrenciaHechoModel]:
    return session.get( RecurrenciaHechoModel, idRecurrenciaHecho)


def create(session: Session, recurrencia:  RecurrenciaHechoModel) ->  RecurrenciaHechoModel:
    session.add(recurrencia)
    session.commit()
    session.refresh(recurrencia)
    return recurrencia


def update(session: Session, recurrencia:  RecurrenciaHechoModel) ->  RecurrenciaHechoModel:
    session.add(recurrencia)
    session.commit()
    session.refresh(recurrencia)
    return recurrencia


def delete(session: Session, recurrencia:  RecurrenciaHechoModel):
    session.delete(recurrencia)
    session.commit()