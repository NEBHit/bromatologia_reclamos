from datetime import datetime, time
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

# Importar el link_model en tiempo de ejecución
from models.reclamoCategoria_model import ReclamoCategoriaModel

if TYPE_CHECKING:
    from models.categoria_model import CategoriaModel
    from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel
    from models.estadoReclamo_model import EstadoReclamoModel
    from models.evidencia_model import EvidenciaModel
    from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel
    from models.localidad_model import LocalidadModel
    from models.usuario_model import UsuarioModel
    from models.inspector_model import InspectorModel
    from models.recurrenciaHecho_model import RecurrenciaHechoModel


class ReclamoModel(SQLModel, table=True):
    __tablename__ = "Reclamo"

    # Clave primaria
    idReclamo: Optional[int] = Field(default=None, primary_key=True)
    nroExpediente: str = Field(max_length=30, unique=True, index=True, nullable=False)
    comercioNombre: str = Field(max_length=150, nullable=False)
    idLocalidad: int = Field(foreign_key="Localidad.idLocalidad", nullable=False)
    calle: str = Field(max_length=250, nullable=False) 
    latitud: Optional[float] = Field(default=None)
    longitud: Optional[float] = Field(default=None)
    
    # Teléfonos comercio
    areaCelComercio: Optional[int] = Field(default=None)
    nroCelComercio: Optional[int] = Field(default=None)

    # Horarios comercio (En MariaDB son nullable)
    horaAperturaComercio: Optional[datetime] = Field(default=None, nullable=True)
    horaCierreComercio: Optional[datetime] = Field(default=None, nullable=True)
    
    # Detalle adicional de categoría
    categoriaDetalle: Optional[str] = Field(default=None, max_length=255)

    # Hecho denunciado
    prioridad: bool = Field(nullable=False)
    fechaHoraHecho: datetime = Field(nullable=False)
    idRecurrenciaHecho: Optional[int] = Field(
        default=None, foreign_key="RecurrenciaHecho.idRecurrenciaHecho", nullable=True
    )
    incidenteHecho: Optional[str] = Field(default=None, max_length=255)
    
    # Datos del denunciante
    esAnonimo: bool = Field(default=False, nullable=False)
    nomDenunciante: Optional[str] = Field(default=None, max_length=120)
    apeDenunciante: Optional[str] = Field(default=None, max_length=120)
    areaCelDenunciante: Optional[int] = Field(default=None)
    nroCelDenunciante: Optional[int] = Field(default=None)
    emailDenunciante: Optional[str] = Field(default=None, max_length=120)
    aceptaDeclaracionJurada: bool = Field(default=True, nullable=False)

    # Estado y auditoría interna
    idEstadoActual: int = Field(default=1, foreign_key="EstadoReclamo.idEstadoReclamo", nullable=False)
    idInspector: Optional[int] = Field(default=None, foreign_key="Inspector.idInspector")
    idUsuarioCrear: Optional[int] = Field(default=None, foreign_key="Usuario.idUsuario")
    idUsuarioMod: Optional[int] = Field(default=None, foreign_key="Usuario.idUsuario")

    # Timestamps del sistema
    fechaIngresoSistema: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), nullable=True),
    )
    fechaMod: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            onupdate=func.now(),
            nullable=True,
        ),
    )

    # Relaciones maestras
    localidad: Optional["LocalidadModel"] = Relationship(back_populates="reclamos")
    recurrencia: Optional["RecurrenciaHechoModel"] = Relationship(back_populates="reclamos")  
    estado_actual: Optional["EstadoReclamoModel"] = Relationship(back_populates="reclamos")
    inspector: Optional["InspectorModel"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ReclamoModel.idInspector]"},
    )

    # Relación N a N con Categorías
    categorias: List["CategoriaModel"] = Relationship(
        back_populates="reclamos",
        link_model=ReclamoCategoriaModel,
    )
     
    # Relaciones satélites
    detalle_alimento: Optional["DetalleAlimentoReclamoModel"] = Relationship(back_populates="reclamo")
    evidencias: List["EvidenciaModel"] = Relationship(back_populates="reclamo")
    historial: List["HistorialEstadoReclamoModel"] = Relationship(
        back_populates="reclamo",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        from_attributes = True