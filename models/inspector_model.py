from sqlmodel import SQLModel, Field,Relationship
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from typing import List, TYPE_CHECKING

#if TYPE_CHECKING:
#   from models.expediente_inspector_estadoInspeccion_model import Expediente_Inspector_EstadoInspeccionModel

class InspectorModel(SQLModel, table=True):
    __tablename__ = "Inspector"
    
    idInspector: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, nullable=False)
    apellido: str | None = Field(default=None, nullable=True)

    idUsuarioCrear: int = Field(default=None, foreign_key="Usuario.idUsuario", nullable=False)
    fechaIngresoSistema: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))

   # estados_inspeccion: List["Expediente_Inspector_EstadoInspeccionModel"] = Relationship(back_populates="inspector")

    class Config:
        from_attributes = True    