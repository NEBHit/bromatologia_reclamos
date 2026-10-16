from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from models.reclamo_model import ReclamoModel


class RecurrenciaHechoModel(SQLModel, table=True):
  __tablename__ = "RecurrenciaHecho"

  idRecurrenciaHecho: Optional[int] = Field(default=None, primary_key=True)
  nombre: str = Field(nullable=False, max_length=50)
  descripcion: Optional[str] = Field(default=None)
  orden: int = Field(default=None)

  # Relación inversa hacia reclamos
  reclamos: List["ReclamoModel"] = Relationship(back_populates="recurrencia")

  class Config:
    from_attributes = True