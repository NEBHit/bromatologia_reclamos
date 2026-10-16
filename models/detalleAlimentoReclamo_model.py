from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.reclamo_model import ReclamoModel


class DetalleAlimentoReclamoModel(SQLModel, table=True):
  __tablename__ = "DetalleAlimentoReclamo"

  idDetalleAlimento: Optional[int] = Field(default=None, primary_key=True)
  idReclamo: int = Field(foreign_key="Reclamo.idReclamo", nullable=False)
  productoNombreMarca: str = Field(max_length=200, nullable=False)
  fechaVencimiento: Optional[str] = Field(default=None)
  nroLote: Optional[str] = Field(default=None, max_length=100)
  estadoConservacion: str = Field(nullable=False)

  # Relación con el reclamo principal
  reclamo: Optional["ReclamoModel"] = Relationship(
      back_populates="detalle_alimento"
  )

  class Config:
    from_attributes = True