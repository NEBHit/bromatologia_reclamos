from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

from models.reclamoCategoria_model import ReclamoCategoriaModel
from models.reclamo_model import ReclamoModel

class CategoriaModel(SQLModel, table=True):
  __tablename__ = "Categoria"

  idCategoria: Optional[int] = Field(default=None, primary_key=True)
  nombre: str = Field(nullable=False, max_length=150, index=True)
  requiereDetalle: bool = Field(default=False)
  orden: int = Field(default=0)
  activa: bool = Field(default=True)

 # Relación N a N hacia Reclamos
  reclamos: List["ReclamoModel"] = Relationship(
        back_populates="categorias",
        link_model=ReclamoCategoriaModel
  )

  class Config:
    from_attributes = True