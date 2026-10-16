from models.categoria_model import CategoriaModel
from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel
from models.estadoReclamo_model import EstadoReclamoModel
from models.evidencia_model import EvidenciaModel
from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel
from models.localidad_model import LocalidadModel
from models.reclamo_model import ReclamoModel
from models.reclamoCategoria_model import ReclamoCategoriaModel
from models.usuario_model import UsuarioModel
from models.recurrenciaHecho_model import RecurrenciaHechoModel

__all__ = [
    "LocalidadModel",
    "CategoriaModel",
    "EstadoReclamoModel",
    "UsuarioModel",
    "ReclamoModel",
    "ReclamoCategoriaModel",
    "DetalleAlimentoReclamoModel",
    "EvidenciaModel",
    "HistorialEstadoReclamoModel",
    "RecurrenciaHechoModel"
]