from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func
from datetime import datetime


class UsuarioModel(SQLModel, table=True):
    __tablename__ = "Usuario"
    
    idUsuario: int | None = Field(default=None, primary_key=True)
    usuario: str = Field(index=True, nullable=False)
    clave: str = Field(default=None, nullable=False)
    activo: int = Field(default=1, nullable=False)
    idRol: int = Field(default=1, nullable=False) # por el momento este valor no se usa, todos los usuarios hacen todo
    fechaUltimoLogin: datetime = Field(sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))

    class Config:
        from_attributes = True    
