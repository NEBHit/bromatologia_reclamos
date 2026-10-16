from sqlmodel import SQLModel, Field, Relationship
from typing import List,TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
     from models.expediente_model import ExpedienteModel

class CategoriaReclamo(SQLModel, table=True):
    __tablename__ = "CategoriaReclamo"
    
    idCategoriaReclamo: int|None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, nullable=False)
    requiereDetalle: bool = False
    orden: int = 0
    activa: bool = True
        
    class Config:
        from_attributes = True    
