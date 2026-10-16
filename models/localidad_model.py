from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.reclamo_model import ReclamoModel


class LocalidadModel(SQLModel, table=True):
  __tablename__ = "Localidad"

  idLocalidad: Optional[int] = Field(default=None, primary_key=True)
  nombre: str = Field(nullable=False, max_length=50)
  codPostal: Optional[int] = Field(default=None)

  # Relación inversa hacia reclamos
  reclamos: List["ReclamoModel"] = Relationship(back_populates="localidad")

  class Config:
    from_attributes = True