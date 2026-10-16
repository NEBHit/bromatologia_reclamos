from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel
  from models.reclamo_model import ReclamoModel  

class UsuarioModel(SQLModel, table=True):
  __tablename__ = "Usuario"

  idUsuario: Optional[int] = Field(default=None, primary_key=True)
  usuario: str = Field(nullable=False, max_length=50, unique=True)
  clave: str = Field(nullable=False, max_length=255)
  idRol: int = Field(default=1)

  fechaCreacion: Optional[datetime] = Field(
      default=None,
      sa_column=Column(DateTime, server_default=func.now(), nullable=False),
  )
  fechaModificacion: Optional[datetime] = Field(
      default=None,
      sa_column=Column(
          DateTime,
          server_default=func.now(),
          onupdate=func.now(),
          nullable=False,
      ),
  )
  fechaUltimoLogin: Optional[datetime] = Field(default=None)
  activo: bool = Field(default=True)
 
  
  # Relación únicamente con historial:
  historiales: List["HistorialEstadoReclamoModel"] = Relationship(
        back_populates="usuario"
    )

  class Config:
        from_attributes = True