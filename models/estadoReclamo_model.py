from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel
  from models.reclamo_model import ReclamoModel


class EstadoReclamoModel(SQLModel, table=True):
  __tablename__ = "EstadoReclamo"

  idEstadoReclamo: Optional[int] = Field(default=None, primary_key=True)
  nombre: str = Field(nullable=False, max_length=60)
  descripcion: Optional[str] = Field(default=None, max_length=255)

  colorBadge: Optional[str] = Field(default="bg-secondary text-white") # Para mostrar en las grillas los estados con distintos colores

  # Relaciones
  reclamos: List["ReclamoModel"] = Relationship(back_populates="estado_actual")
  historiales: List["HistorialEstadoReclamoModel"] = Relationship(
      back_populates="estado"
  )
  

  class Config:
    from_attributes = True