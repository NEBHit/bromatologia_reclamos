from typing import Optional
from sqlmodel import SQLModel, Field

class ReclamoCategoriaModel(SQLModel, table=True):
  __tablename__ = "ReclamoCategoria"

  idReclamo: Optional[int] = Field(
        default=None,
        foreign_key="Reclamo.idReclamo",
        primary_key=True,
        nullable=False
    )
  idCategoria: Optional[int] = Field(
        default=None,
        foreign_key="Categoria.idCategoria",
        primary_key=True,
        nullable=False
    )

  class Config:
    from_attributes = True