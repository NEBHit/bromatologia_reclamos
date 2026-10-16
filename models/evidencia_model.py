from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.reclamo_model import ReclamoModel


class EvidenciaModel(SQLModel, table=True):
  __tablename__ = "Evidencia"

  idEvidencia: Optional[int] = Field(default=None, primary_key=True)
  idReclamo: int = Field(foreign_key="Reclamo.idReclamo", nullable=False)
  nombreArchivo: str = Field(max_length=255, nullable=False)
  rutaAlmacenamiento: str = Field(max_length=500, nullable=False)
  tipoMime: str = Field(max_length=100, nullable=False)
  tamanoBytes: int = Field(nullable=False)
  fechaSubida: Optional[datetime] = Field(
      default=None,
      sa_column=Column(DateTime, server_default=func.now(), nullable=False),
  )

  reclamo: Optional["ReclamoModel"] = Relationship(back_populates="evidencias")

  class Config:
    from_attributes = True