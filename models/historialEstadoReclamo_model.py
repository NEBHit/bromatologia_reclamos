from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime, func, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.estadoReclamo_model import EstadoReclamoModel
    from models.reclamo_model import ReclamoModel
    from models.usuario_model import UsuarioModel


class HistorialEstadoReclamoModel(SQLModel, table=True):
    __tablename__ = "HistorialEstadoReclamo"

    idHistorial: Optional[int] = Field(default=None, primary_key=True)
    idReclamo: int = Field(foreign_key="Reclamo.idReclamo", nullable=False)
    idEstadoReclamo: int = Field(foreign_key="EstadoReclamo.idEstadoReclamo", nullable=False)
    idUsuario: Optional[int] = Field(default=None, foreign_key="Usuario.idUsuario")
    
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    
    fechaHistorial: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False)
    )

    # Relaciones hacia las tablas padre
    reclamo: Optional["ReclamoModel"] = Relationship(back_populates="historial")
    estado: Optional["EstadoReclamoModel"] = Relationship(back_populates="historiales")

    usuario: Optional["UsuarioModel"] = Relationship(back_populates="historiales")

    class Config:
        from_attributes = True